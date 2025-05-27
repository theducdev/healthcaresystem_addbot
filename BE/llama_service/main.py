import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pyttsx3
from ctransformers import AutoModelForCausalLM
import uvicorn
from pydantic import BaseModel

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 160)

# Model configuration
MODEL_ID = "TheBloke/Llama-2-7B-Chat-GGML"
print("🔄 Đang tải mô hình LLaMA...")

try:
    # Sử dụng ctransformers để tải mô hình GGML
    llm = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        model_type="llama",
        gpu_layers=0,  # Đặt là 0 để chạy trên CPU
        context_length=2048,  # Độ dài context
        max_new_tokens=256,  # Số tokens tối đa cho mỗi phản hồi
        temperature=0.7,  # Độ đa dạng của câu trả lời
        top_p=0.95,
        repetition_penalty=1.15
    )
    print("✅ Mô hình đã sẵn sàng!")
except Exception as e:
    print(f"❌ Lỗi khi tải mô hình: {str(e)}")
    raise

class ChatRequest(BaseModel):
    message: str
    should_speak: bool = False

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Tạo prompt cho LLama
        prompt = f"""<s>[INST] You are a medical assistant. The user reports the following symptoms: {request.message}
Based on common illnesses (Flu, Cold, COVID-19, Allergy), which one is most likely?
Suggest a test and recommend suitable medicine.
Please respond in Vietnamese. [/INST]"""

        # Lấy phản hồi từ mô hình
        response = llm(prompt, max_new_tokens=256)
        
        # Xử lý response để lấy phần trả lời sau prompt
        response = response.split("[/INST]")[-1].strip()

        # Nếu yêu cầu đọc văn bản
        if request.should_speak:
            engine.say(response)
            engine.runAndWait()

        return {"response": response}
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True) 