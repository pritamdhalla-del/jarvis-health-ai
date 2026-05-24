from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from agent import run_agent

app = FastAPI()

# CORS FIX FOR VERCEL FRONTEND
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROOT API
@app.get("/")
def root():
    return {"message": "JARVIS Backend Running"}

# CHAT API
@app.get("/chat")
def chat(query: str):

    response = run_agent(query)

    return {
        "response": response
    }

# DOWNLOAD DOCUMENT API
@app.get("/download/{filename}")
def download_file(filename: str):

    return FileResponse(
        path=filename,
        filename=filename,
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )