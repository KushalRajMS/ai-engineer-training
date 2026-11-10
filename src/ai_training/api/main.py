from fastapi import FastAPI, HTTPException, UploadFile, File
from ai_training.api.models import AskRequest, AskResponse, IngestResponse
from importlib.metadata import version as pkg_version
from ai_training.langchain_basics.rag import run_rag_with_sources
from ai_training.langchain_basics.chains import make_llm
from ai_training.langchain_basics.embeddings import make_embedder
from ai_training.langchain_basics.vector_store import load_vector_store, make_retriever
from pathlib import Path
from ai_training.config import ARTIFACTS_DIR, MAX_FILE_SIZE
from functools import lru_cache
from fastapi.concurrency import run_in_threadpool
from ai_training.api.services import build_store

app= FastAPI(
    title= "Ask My Docs API",
    description= "API helps to get you the information from the provided source."
)

@lru_cache(maxsize=1)
def get_embedder():
    return make_embedder()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/version")
def version():
    return {"version": pkg_version("ai-engineer-training")}

@app.post("/ask", response_model= AskResponse)
def ask(request: AskRequest):
    store= ARTIFACTS_DIR / "vector_store"
    if not store.is_dir():
        raise HTTPException(
            status_code=404,
            detail= "Vector store not found."
        )
    embedder= get_embedder()
    try:
        vector_store= load_vector_store(str(store), embedder)
    except Exception:
        raise HTTPException(status_code=500, detail="Couldnt load vector store.")
    retriever= make_retriever(vector_store, k=request.k)
    llm= make_llm()
    try:
        result= run_rag_with_sources(retriever, request.question, llm)
    except Exception:
        raise HTTPException(status_code=502, detail="Language model request failed.")
    return result

@app.post("/ingest", response_model= IngestResponse)
async def ingest(file: UploadFile = File(...)):
    if not file.filename or not file.filename.strip():
        raise HTTPException(
            status_code=400,
            detail="File name can not be blank."
        )
    file_obj= Path(file.filename)
    if file_obj.suffix.lower() not in [".txt", ".pdf"]:
        raise HTTPException(
            status_code=415,
            detail= "Allowed file extension are .txt and .pdf."
        )
    content= await file.read(MAX_FILE_SIZE + 1)
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code= 413,
            detail="File sized exceeded 5 MB."
        )
    filename= file_obj.name
    upload_store= ARTIFACTS_DIR / "uploads"
    vector_path= ARTIFACTS_DIR / "vector_store"
    upload_store.mkdir(parents=True, exist_ok=True)
    upload_filepath= upload_store / filename
    with open(upload_filepath, "wb") as f:
        f.write(content)
    try:
        count= await run_in_threadpool(build_store, str(upload_store), str(vector_path), get_embedder())
    except HTTPException:
        upload_filepath.unlink(missing_ok=True)
        raise
    except ValueError:
        upload_filepath.unlink(missing_ok=True)
        raise HTTPException(
            status_code=400,
            detail="Upload file can not be empty."
        )
    except Exception:
        upload_filepath.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail="Couldn't create vector store."
        )
    return {
        "filename": filename,
        "chunks": count,
        "message": "Vector stored successfully."
    }