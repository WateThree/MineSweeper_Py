CUDA_VISIBLE_DEVICES=0 \
swift rlhf \
    --rlhf_type grpo \
    --model deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B \
    --external_plugins examples/train/grpo/plugin/plugin.py \
    --reward_funcs MineSweeperReward LengthReward \
    --train_type lora \
    --lora_rank 8 \
    --lora_alpha 32 \
    --target_modules all-linear \
    --torch_dtype bfloat16 \
    --dataset '/mnt/workspace/ms-swift/MineSweeperData.jsonl#200' \
    --max_completion_length 2048\
    --num_train_epochs 1 \
    --per_device_train_batch_size 2 \
    --per_device_eval_batch_size 2 \
    --learning_rate 1e-5 \
    --gradient_accumulation_steps 1 \
    --eval_steps 100 \
    --save_steps 100 \
    --save_total_limit 2 \
    --logging_steps 5 \
    --max_length 2048 \
    --output_dir output \
    --warmup_ratio 0.05 \
    --dataloader_num_workers 2 \
    --dataset_num_proc 2 \
    --num_generations 2 \
    --temperature 0.9 \
    --system 'examples/train/grpo/prompt.txt' \
    --log_completions true