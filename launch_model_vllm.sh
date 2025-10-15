#!/bin/bash

hf_model_path=./weights/DotsOCR          # путь к весам
model_name=dots_ocr                      # имя сервируемой модели
gpu_memory_utilization=0.30              # не забивать VRAM на 100%
tensor_parallel_size=1                   # 1 GPU
port=8000                                # порт сервера vLLM



# === Проверка: есть ли уже запущенный процесс vLLM с этой моделью ===
existing_pid=$(ps aux | grep -i "vllm serve .*${hf_model_path}" | grep -v grep | awk '{print $2}')

if [ -n "$existing_pid" ]; then
    echo "Модель '${model_name}' уже запущена (PID=$existing_pid)."
    exit 0
fi

# === Регистрация модели в vLLM (один раз) ===
export PYTHONPATH=$(dirname "$hf_model_path"):$PYTHONPATH
export CUDA_VISIBLE_DEVICES=0
sed -i '/^from vllm\.entrypoints\.cli\.main import main$/a\
from DotsOCR import modeling_dots_ocr_vllm' "$(which vllm)"

# === Запуск сервера vLLM ===
echo "Запуск модели '${model_name}'..."
nohup vllm serve ${hf_model_path} \
  --tensor-parallel-size ${tensor_parallel_size} \
  --gpu-memory-utilization ${gpu_memory_utilization} \
  --port ${port} \
  --chat-template-content-format string \
  --served-model-name ${model_name} \
  --trust-remote-code > vllm.log 2>&1 &

# === Сохранение PID ===
echo $! > vllm.pid
echo "Модель '${model_name}' запущена в фоне (PID=$(cat vllm.pid)). Логи: vllm.log"

# kill $(cat vllm.pid) убивает процесс