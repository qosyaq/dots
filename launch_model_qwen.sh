#!/bin/bash

hf_model_path=./weights/Qwen-14B         # путь к весам
model_name=qwen-14b                      # имя сервируемой модели
gpu_memory_utilization=0.95             # не забивать VRAM на 100%
tensor_parallel_size=1                   # 1 GPU
port=8001                                # порт сервера



# === Проверка: есть ли уже запущенный процесс с этой моделью ===
existing_pid=$(ps aux | grep -i "vllm serve .*${hf_model_path}" | grep -v grep | awk '{print $2}')

if [ -n "$existing_pid" ]; then
    echo "Модель '${model_name}' уже запущена (PID=$existing_pid)."
    exit 0
fi

# === Регистрация модели в (один раз) ===
export PYTHONPATH=$(dirname "$hf_model_path"):$PYTHONPATH
export CUDA_VISIBLE_DEVICES=0

# === Запуск сервера ===
echo "Запуск модели '${model_name}'..."
nohup vllm serve ${hf_model_path} \
  --tensor-parallel-size ${tensor_parallel_size} \
  --gpu-memory-utilization ${gpu_memory_utilization} \
  --port ${port} \
  --chat-template-content-format string \
  --served-model-name ${model_name} \
  --trust-remote-code > qwen.log 2>&1 &

# === Сохранение PID ===
echo $! > qwen.pid
echo "Модель '${model_name}' запущена в фоне (PID=$(cat qwen.pid)). Логи: qwen.log"

# kill $(cat qwen.pid) убивает процесс