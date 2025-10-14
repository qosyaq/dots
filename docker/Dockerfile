FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3.12 python3.12-venv python3-pip git wget curl build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python3.12 -m ensurepip
RUN python3.12 -m pip install --upgrade pip setuptools wheel

RUN python3.12 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip
RUN pip install torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 \
    --index-url https://download.pytorch.org/whl/cu128

RUN pip install vllm==0.10.0 --extra-index-url https://download.pytorch.org/whl/cu128

RUN pip install https://github.com/Dao-AILab/flash-attention/releases/download/v2.8.2/flash_attn-2.8.2+cu12torch2.7cxx11abiFALSE-cp312-cp312-linux_x86_64.whl

RUN pip install transformers==4.53.2

WORKDIR /workspace

CMD ["/bin/bash"]
