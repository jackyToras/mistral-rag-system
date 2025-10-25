from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
import shutil
from utils import process_and_embed, save_to_chromadb, answer_query, get_chroma_client, get_supported_formats
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

client = get_chroma_client()
COLLECTION_NAME = "documents"


class Question(BaseModel):
    question: str


@app.get("/")
async def root():
    return {
        "message": "RAG Document Q&A System API",
        "status": "running",
        "supported_formats": get_supported_formats()
    }


@app.get("/supported-formats")
async def supported_formats():
    """Return list of supported file formats"""
    return {"formats": get_supported_formats()}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    file_ext = os.path.splitext(file.filename)[-1].lower().replace(".", "")
    supported = get_supported_formats()

    if file_ext not in supported:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Supported formats: {', '.join(supported)}"
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        embedded_chunks = process_and_embed(file_path)
        save_to_chromadb(embedded_chunks, client=client, collection_name=COLLECTION_NAME)

        return {
            "filename": file.filename,
            "total_chunks": len(embedded_chunks),
            "message": "File uploaded and processed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@app.post("/query")
async def query_question(request: Question):
    try:
        answer = answer_query(request.question, client=client, collection_name=COLLECTION_NAME)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "supported_formats": get_supported_formats()
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)