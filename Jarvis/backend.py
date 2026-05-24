from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from agent import run_agent

app = FastAPI()

# Allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chat API
@app.get("/chat")
def chat(query: str):

    response = run_agent(query)

    return {
        "response": response
    }
@app.get("/download")
def download_file():

    path = "jarvis_report.docx"

    return FileResponse(
        path,
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        filename="jarvis_report.docx"
    )