CUDA_VISIBLE_DEVICES=0 swift deploy \
    --model deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B \
    --infer_backend vllm \
    --max_new_tokens 2048 \
    --torch_dtype bfloat16 \
    --served_model_name DeepSeek-R1-Distill-Qwen-1.5B