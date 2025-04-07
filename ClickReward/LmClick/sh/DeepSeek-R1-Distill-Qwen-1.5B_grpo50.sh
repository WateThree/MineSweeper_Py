CUDA_VISIBLE_DEVICES=0 swift deploy \
    --model deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B \
    --adapters output/v32-20250407-105904/checkpoint-49 \
    --infer_backend vllm \
    --torch_dtype bfloat16 \
    --max_new_tokens 2048 \
    --served_model_name DeepSeek-R1-Distill-Qwen-1.5B_grpo50
    