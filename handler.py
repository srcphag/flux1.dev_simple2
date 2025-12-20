# In your handler.py file, modify the output section:

def generate(job):
    # ... your existing code ...
    
    # Instead of returning base64, return file paths or URLs
    output_files = []
    
    output_dir = "/endpoints/output/"
    
    for filename in os.listdir(output_dir):
        if filename.startswith("endpointfile"):  # Your filename_prefix
            file_path = os.path.join(output_dir, filename)
            
            # Option A: Return just the path (client needs direct access)
            output_files.append({
                "path": file_path,
                "filename": filename
            })
            
            # Option B: Upload to a CDN/S3 and return URL
            # url = upload_to_s3(file_path)
            # output_files.append({"url": url})
    
    return {
        "images": output_files
    }