import os
import httpx
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

# Initialize the FastAPI app - This is the "app" attribute Uvicorn is looking for
app = FastAPI(title="Spice Bot API")

# Enable CORS for Flutter development
# This allows your mobile/web app to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Configuration
# GEMINI_API_KEY will be provided by the execution environment
GEMINI_API_KEY = "" 
GEMINI_MODEL = "gemini-2.5-flash-preview-09-2025"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

class ChatRequest(BaseModel):
    query: str

async def call_gemini_with_grounding(user_query: str):
    """
    Calls Gemini with Google Search grounding for real-time information.
    Includes exponential backoff for reliability during high-frequency updates.
    """
    payload = {
        "contents": [{
            "parts": [{"text": user_query}]
        }],
        "tools": [{"google_search": {}}],
        "systemInstruction": {
            "parts": [{
                "text": (
                    "You are Spice Bot, a high-frequency, real-time data assistant. "
                    "Provide accurate, timely updates on breaking news, social trends, "
                    "financial markets, and weather. Use your search grounding tools "
                    "to ensure you have the absolute latest info. Be concise and professional. "
                    "Format responses clearly for a chat interface."
                )
            }]
        }
    }

    retries = 5
    for i in range(retries):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(API_URL, json=payload)
                response.raise_for_status()
                result = response.json()
                
                # Extract text response safely
                candidates = result.get("candidates", [])
                if not candidates:
                    raise ValueError("No candidates returned from API")
                
                text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                
                # Extract grounding sources if available for verification
                grounding_metadata = candidates[0].get("groundingMetadata", {})
                sources = []
                if "groundingAttributions" in grounding_metadata:
                    for attr in grounding_metadata["groundingAttributions"]:
                        web_info = attr.get("web", {})
                        if web_info.get("uri"):
                            sources.append({
                                "title": web_info.get("title", "Source"),
                                "url": web_info.get("uri")
                            })
                
                return {"reply": text, "sources": sources}

        except Exception as e:
            if i == retries - 1:
                # After final retry, return a formal error
                raise HTTPException(status_code=500, detail=f"API connection failed: {str(e)}")
            # Wait for 1s, 2s, 4s, 8s, 16s before retrying
            await asyncio.sleep(2**i)

@app.get("/chat")
async def chat_get(q: str):
    """
    Endpoint for GET requests (matching common simple Flutter API services)
    """
    if not q:
        raise HTTPException(status_code=400, detail="Query is required")
    return await call_gemini_with_grounding(q)

@app.post("/chat")
async def chat_post(request: ChatRequest):
    """
    Standard POST endpoint for structured queries
    """
    return await call_gemini_with_grounding(request.query)

@app.get("/health")
async def health_check():
    """Simple endpoint to verify backend status"""
    return {"status": "online", "model": GEMINI_MODEL}

if __name__ == "__main__":
    import uvicorn
    # This block allows running the file directly with 'python main.py'
    uvicorn.run(app, host="0.0.0.0", port=8000)