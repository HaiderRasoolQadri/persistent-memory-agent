from fastapi import FastAPI
from pydantic import BaseModel
from agent import PersistentMemoryAgent

app=FastAPI(title="Persistent Memory Agent API")
agent=PersistentMemoryAgent()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str 

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    reply=agent.chat(request.message)
    return ChatResponse(reply=reply)

@app.get("/facts")
def get_facts():
    return agent.semantic.get_all_facts()