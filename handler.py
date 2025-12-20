import runpod
import json
import requests
import os
import glob
from pathlib import Path

# ComfyUI API endpoint (runs on the same worker)
COMFYUI_API = "http://127.0.0.1:8188"

def execute_workflow(workflow):
    """Execute ComfyUI workflow and return output files"""
    
    # Submit workflow to ComfyUI
    response = requests.post(
        f"{COMFYUI_API}/prompt",
        json={"prompt": workflow}
    )
    
    if response.status_code != 200:
        raise Exception(f"ComfyUI API error: {response.text}")
    
    result = response.json()
    prompt_id = result.get("prompt_id")
    
    if not prompt_id:
        raise Exception("No prompt_id returned from ComfyUI")
    
    # Wait for completion and get output files
    return wait_for_completion(prompt_id)

def wait_for_completion(prompt_id, timeout=600):
    """Wait for ComfyUI to complete and return output file paths"""
    import time
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        # Check history for completed job
        history_response = requests.get(f"{COMFYUI_API}/history/{prompt_id}")
        
        if history_response.status_code == 200:
            history = history_response.json()
            
            if prompt_id in history:
                job_data = history[prompt_id]
                
                # Check if job completed
                if "outputs" in job_data:
                    output_files = []
                    
                    # Extract file information from outputs
                    for node_id, node_output in job_data["outputs"].items():
                        if "images" in node_output:
                            for img in node_output["images"]:
                                filename = img.get("filename")
                                subfolder = img.get("subfolder", "")
                                
                                if filename:
                                    # Construct full path
                                    if subfolder:
                                        file_path = f"/workspace/ComfyUI/output/{subfolder}/{filename}"
                                    else:
                                        file_path = f"/workspace/ComfyUI/output/{filename}"
                                    
                                    output_files.append({
                                        "filename": filename,
                                        "path": file_path,
                                        "subfolder": subfolder
                                    })
                    
                    return output_files
        
        time.sleep(2)  # Poll every 2 seconds
    
    raise Exception(f"Timeout waiting for prompt {prompt_id}")

def upload_to_storage(file_path, storage_type="network_volume"):
    """
    Upload file to storage and return URL
    Currently supports network volume paths
    TODO: Add S3 upload support
    """
    
    if storage_type == "network_volume":
        # Files are already on network volume
        # Return the path (client needs to access volume directly)
        return {
            "type": "network_volume",
            "path": file_path,
            "message": "File saved on network volume"
        }
    
    elif storage_type == "s3":
        # TODO: Implement S3 upload
        # Example:
        # import boto3
        # s3 = boto3.client('s3')
        # bucket = os.environ.get('S3_BUCKET_NAME')
        # s3.upload_file(file_path, bucket, os.path.basename(file_path))
        # return f"https://{bucket}.s3.amazonaws.com/{os.path.basename(file_path)}"
        raise NotImplementedError("S3 upload not implemented yet")
    
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")

def handler(job):
    """
    Main handler function for RunPod
    Processes ComfyUI workflow and returns image locations
    """
    
    job_input = job["input"]
    
    # Validate input
    if "workflow" not in job_input:
        return {
            "error": "Missing 'workflow' in input. Please provide a ComfyUI workflow."
        }
    
    workflow = job_input["workflow"]
    storage_type = job_input.get("storage_type", "network_volume")
    
    try:
        # Execute workflow
        runpod.serverless.progress_update(job, "Executing ComfyUI workflow...")
        output_files = execute_workflow(workflow)
        
        if not output_files:
            return {
                "error": "No output files generated"
            }
        
        # Process output files
        runpod.serverless.progress_update(job, f"Processing {len(output_files)} output file(s)...")
        results = []
        
        for file_info in output_files:
            file_path = file_info["path"]
            
            # Verify file exists
            if os.path.exists(file_path):
                storage_info = upload_to_storage(file_path, storage_type)
                results.append({
                    "filename": file_info["filename"],
                    "storage": storage_info
                })
            else:
                results.append({
                    "filename": file_info["filename"],
                    "error": f"File not found: {file_path}"
                })
        
        return {
            "status": "success",
            "files": results,
            "message": f"Generated {len(results)} image(s)"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed"
        }

# Start the serverless function
runpod.serverless.start({
    "handler": handler
})