FROM python:3.9-slim

WORKDIR /app

# Cài đặt các dependencies system cần thiết
RUN apt-get update && apt-get install -y \
    espeak \
    build-essential \
    cmake \
    git \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements và cài đặt
COPY requirements.txt .

# Cài đặt ctransformers từ source và các dependencies
RUN pip install --no-cache-dir numpy torch --no-deps && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir ctransformers --no-deps && \
    pip install --no-cache-dir ctransformers[cuda] --no-deps

# Copy source code
COPY . .

# Tải mô hình LLaMA trước
RUN python -c "from ctransformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('TheBloke/Llama-2-7B-Chat-GGML', model_type='llama')"

# Expose port
EXPOSE 8001

# Run the application
CMD ["python", "main.py"] 