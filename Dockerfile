# clean base image containing only comfyui, comfy-cli and comfyui-manager
FROM runpod/worker-comfyui:5.5.0-base

# install custom nodes into comfyui
RUN comfy node install --exit-on-fail rgthree-comfy@1.0.2512112053
RUN comfy node install --exit-on-fail was-node-suite-comfyui@1.0.2

# download models into comfyui
RUN comfy model download --url https://huggingface.co/Kijai/flux-fp8/resolve/main/flux1-dev-fp8.safetensors --relative-path models/diffusion_models --filename flux1-dev-fp8.safetensors
RUN comfy model download --url https://huggingface.co/srcphag/Flux1-Depth-Dev/resolve/main/vae/diffusion_pytorch_model.safetensors --relative-path models/vae --filename diffusion_pytorch_model.safetensors
RUN comfy model download --url https://huggingface.co/Comfy-Org/stable-diffusion-3.5-fp8/resolve/main/text_encoders/clip_l.safetensors --relative-path models/clip --filename clip_l.safetensors
RUN comfy model download --url https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors --relative-path models/clip --filename t5xxl_fp8_e4m3fn.safetensors
RUN comfy model download --url https://huggingface.co/srcphag/Flux1.Dev_Loras/resolve/main/External/amateurphoto-v6-forcu.safetensors --relative-path models/loras --filename amateurphoto-v6-forcu.safetensors
RUN comfy model download --url https://huggingface.co/srcphag/Flux1.Dev_Loras/resolve/main/Fish/ScomberScombrus.safetensors --relative-path models/loras --filename ScomberScombrus.safetensors
RUN comfy model download --url https://huggingface.co/RippleLinks/Flux_Models/blob/main/4xNomos2_hq_drct-l.pth --relative-path models/upscale_models --filename 4xNomos2_hq_drct-l.pth

# copy all input data (like images or videos) into comfyui (uncomment and adjust if needed)
