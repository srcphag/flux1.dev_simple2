import requests
import time
import os
from pathlib import Path

# Configuration
API_KEY = "API_KEY"  # Replace with your actual API key
ENDPOINT_ID = "ute4afrar9lkjy"  # Your RunPod endpoint ID
API_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# Your workflow data
workflow_data = {
    "input": {
        "workflow": {
            "3": {
                "inputs": {
                    "seed": 138395551842908,
                    "steps": 15,
                    "cfg": 1,
                    "sampler_name": "ddim",
                    "scheduler": "normal",
                    "denoise": 1,
                    "model": ["63", 0],
                    "positive": ["26", 0],
                    "negative": ["7", 0],
                    "latent_image": ["66", 0]
                },
                "class_type": "KSampler"
            },
            "7": {
                "inputs": {
                    "text": "drawing, painting, non realistic, rust, dirt",
                    "clip": ["63", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "8": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["32", 0]
                },
                "class_type": "VAEDecode"
            },
            "23": {
                "inputs": {
                    "text": ["72", 0],
                    "clip": ["63", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "26": {
                "inputs": {
                    "guidance": 1,
                    "conditioning": ["23", 0]
                },
                "class_type": "FluxGuidance"
            },
            "31": {
                "inputs": {
                    "unet_name": "flux1-dev-fp8.safetensors",
                    "weight_dtype": "default"
                },
                "class_type": "UNETLoader"
            },
            "32": {
                "inputs": {
                    "vae_name": "diffusion_pytorch_model.safetensors"
                },
                "class_type": "VAELoader"
            },
            "34": {
                "inputs": {
                    "clip_name1": "clip_l.safetensors",
                    "clip_name2": "t5xxl_fp8_e4m3fn.safetensors",
                    "type": "flux"
                },
                "class_type": "DualCLIPLoader"
            },
            "41": {
                "inputs": {
                    "filename_prefix": "ComfyUI",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            },
            "63": {
                "inputs": {
                    "lora_01": "None",
                    "strength_01": 1.0,
                    "lora_02": "ScomberScombrus.safetensors",
                    "strength_02": 1.0,
                    "lora_03": "None",
                    "strength_03": 1.0,
                    "lora_04": "None",
                    "strength_04": 1.0,
                    "model": ["31", 0],
                    "clip": ["34", 0]
                },
                "class_type": "Lora Loader Stack (rgthree)"
            },
            "66": {
                "inputs": {
                    "width": 1024,
                    "height": 1024,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "70": {
                "inputs": {
                    "string_a": "a ScomberScombrus fish ",
                    "string_b": ["71", 0],
                    "delimiter": ""
                },
                "class_type": "StringConcatenate"
            },
            "71": {
                "inputs": {
                    "text": "a ScomberScombrus fish over a big white wrap paper in a fish store environment. The paper is located over a green plain chroma key matte background. The lighting and setup suggest this is a fish store space where fishes are cleaned. Cenital Top view camera."
                },
                "class_type": "Text Multiline"
            },
            "72": {
                "inputs": {
                    "string_a": ["70", 0],
                    "string_b": "",
                    "delimiter": ""
                },
                "class_type": "StringConcatenate"
            }
        }
    }
}

def submit_job():
    """Submit the job to RunPod"""
    print("Submitting job to RunPod...")
    response = requests.post(f"{API_URL}/run", headers=headers, json=workflow_data)
    
    if response.status_code == 200:
        job_data = response.json()
        job_id = job_data.get("id")
        print(f"Job submitted successfully! Job ID: {job_id}")
        return job_id
    else:
        print(f"Error submitting job: {response.status_code}")
        print(response.text)
        return None

def check_job_status(job_id):
    """Check the status of a job"""
    response = requests.get(f"{API_URL}/status/{job_id}", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error checking status: {response.status_code}")
        return None

def download_image_from_url(url, filename="output.png"):
    """Download image from URL"""
    script_dir = Path(__file__).parent
    output_path = script_dir / filename
    
    try:
        print(f"Downloading image from: {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ Image saved to: {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ Error downloading image: {e}")
        return None

def get_output_files(job_id):
    """Get list of output files from the job"""
    # In RunPod with network storage, the handler should return file paths or URLs
    # The exact structure depends on your ComfyUI handler implementation
    
    # Option 1: If your handler returns file paths in the network volume
    # You would need to construct the URL to access them
    
    # Option 2: If using RunPod's file serving
    # Images are typically saved in /workspace/ComfyUI/output/
    # and can be accessed via the RunPod API
    
    return None

def main():
    # Submit the job
    job_id = submit_job()
    
    if not job_id:
        return
    
    # Poll for results
    print("\nWaiting for job to complete...")
    max_wait_time = 600  # 10 minutes
    poll_interval = 5  # Check every 5 seconds
    elapsed_time = 0
    
    while elapsed_time < max_wait_time:
        status_data = check_job_status(job_id)
        
        if not status_data:
            break
        
        status = status_data.get("status")
        print(f"Status: {status} (Elapsed: {elapsed_time}s)")
        
        if status == "COMPLETED":
            print("\n✅ Job completed successfully!")
            
            # Extract the output
            output = status_data.get("output", {})
            
            # Check if output contains file paths or URLs
            images_downloaded = False
            
            # Check for message.images structure
            if "message" in output:
                message = output["message"]
                
                # If images are returned as URLs
                if isinstance(message, dict) and "images" in message:
                    images = message["images"]
                    print(f"Found {len(images)} image(s)")
                    
                    for idx, img_data in enumerate(images):
                        filename = f"output_{idx}.png"
                        
                        # Check if it's a URL
                        if isinstance(img_data, str) and img_data.startswith("http"):
                            if download_image_from_url(img_data, filename):
                                images_downloaded = True
                        # Check if it's an object with URL
                        elif isinstance(img_data, dict) and "url" in img_data:
                            if download_image_from_url(img_data["url"], filename):
                                images_downloaded = True
                        # Check if it's a file path that we need to construct URL for
                        elif isinstance(img_data, dict) and "path" in img_data:
                            file_path = img_data["path"]
                            print(f"Output file path: {file_path}")
                            # You would need to know how to access files from your network volume
                            print("ℹ️  File saved on network volume. Access it directly from the pod.")
                        # Otherwise it might still be base64
                        else:
                            print(f"⚠️  Image data is not a URL. It might be base64 or file path.")
                            print(f"Image data type: {type(img_data)}")
                            if isinstance(img_data, str):
                                print(f"First 100 chars: {str(img_data)[:100]}")
                
                # If message contains file paths directly
                elif isinstance(message, dict) and "files" in message:
                    files = message["files"]
                    print(f"Output files: {files}")
                    print("ℹ️  Files are saved on the network volume")
                
                elif isinstance(message, str):
                    print(f"Message: {message}")
            
            # Print output structure for debugging
            if not images_downloaded:
                print("\nℹ️  Output structure:")
                import json
                print(json.dumps(output, indent=2)[:2000])
                
                print("\n" + "="*60)
                print("IMPORTANT: To avoid base64 encoding, you need to:")
                print("1. Modify your RunPod ComfyUI handler to return file URLs")
                print("2. Or configure it to upload to S3 and return S3 URLs")
                print("3. The output files are in: /runpod-volume/ComfyUI/output/")
                print("="*60)
            
            break
        
        elif status == "FAILED":
            print("\n❌ Job failed!")
            print("Error:", status_data.get("error"))
            print("Details:", status_data.get("output", {}).get("details", []))
            break
        
        elif status in ["IN_QUEUE", "IN_PROGRESS"]:
            time.sleep(poll_interval)
            elapsed_time += poll_interval
        
        else:
            print(f"Unknown status: {status}")
            break
    
    if elapsed_time >= max_wait_time:
        print("\n⏱️ Timeout: Job took too long to complete")

if __name__ == "__main__":
    main()