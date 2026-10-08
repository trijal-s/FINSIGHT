from fastapi import FastAPI,HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from chain import ask,ask_stream,build_history

app = FastAPI(
    title="Finsight API",
    description="Annual report intelligence engine",
    version="1.0.0",)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"])

class HistoryItem(BaseModel):
    role: str
    content: str

class AskRequest(BaseModel):
    query: str
    company: Optional[str]= None
    history: list[HistoryItem] = []

class AskResponse(BaseModel):
    answer: str
    company: Optional[str]= None
    query: str

@app.get("/")
async def root():
    return {
        "status": "running",
        "service": "Finsight API",
        "version" : "1.0.0"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }

@app.post("/ask",response_model=AskResponse)
async def ask_endpoint(body: AskRequest):
    try:
        #history
        history=build_history([
            {"role":item.role,"content":item.content} 
            for item in body.history
        ])

        #get answer
        answer=ask(
            query=body.query,
            company=body.company,
            history=history
        )

        return AskResponse(
            answer=answer,
            company=body.company,
            query=body.query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask_stream")
async def ask_stream_endpoint(body: AskRequest):
    try:
        #history
        history=build_history([
            {"role":item.role,"content":item.content} 
            for item in body.history
        ])

        #streaming response
        def event_stream():
            for chunk in ask_stream(
                query=body.query,
                company=body.company,
                history=history
            ):
                yield chunk

        return StreamingResponse(event_stream(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/companies")
async def list_companies():
    try:
        # reuse retriever's Chroma client — a second client on the same
        # path with different settings raises "already exists" error
        from retriever import get_vectorstore

        collection = get_vectorstore()._collection
        all_data   = collection.get(include=["metadatas"])

        companies = list(set(
            meta.get("company", "Unknown")
            for meta in all_data["metadatas"]
            if meta
        ))

        return {
            "companies":    sorted(companies),
            "total_chunks": collection.count(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,   # auto-restart on code changes
    )
    