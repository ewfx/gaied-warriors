from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from document_processor import DocumentProcessor

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],  # Allow requests from live server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process-email")
async def process_email(file: UploadFile = File(...)):
    if not file.filename.endswith('.eml'):
        return {"error": "Only .eml files are supported"}
    
    content = await file.read()
    try:
        processor = DocumentProcessor(os.getenv("OPENAI_API_KEY"))
        result = processor.process_email(content)
        return result
    finally:
        await file.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


