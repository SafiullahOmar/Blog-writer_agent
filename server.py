"""
Blog Writing Agent - FastAPI Backend

Run with: uvicorn server:app --reload
"""

import os
from datetime import date
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import blog agent
from blog_agent import BlogAgent

# Initialize FastAPI app
app = FastAPI(
    title="Blog Writing Agent",
    description="AI-powered technical blog generator",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the blog agent
agent = BlogAgent()


# Request/Response models
class BlogRequest(BaseModel):
    topic: str
    as_of: Optional[str] = None


class BlogResponse(BaseModel):
    success: bool
    blog_title: str
    blog_content: str
    mode: str
    blog_kind: str
    sections_count: int
    word_count: int
    error: Optional[str] = None


# API Routes
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main HTML page."""
    html_path = Path(__file__).parent / "index.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text())
    else:
        return HTMLResponse(content="<h1>index.html not found</h1>", status_code=404)


@app.post("/api/generate", response_model=BlogResponse)
async def generate_blog(request: BlogRequest):
    """Generate a blog post for the given topic."""
    
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    
    try:
        # Set as_of date
        as_of = request.as_of or date.today().isoformat()
        
        # Run the agent
        result = agent.run(
            topic=request.topic,
            as_of=as_of,
            verbose=False
        )
        
        # Extract data
        plan = result["plan"]
        final_content = result.get("final", "")
        
        # Calculate word count
        word_count = len(final_content.split())
        
        return BlogResponse(
            success=True,
            blog_title=plan.blog_title,
            blog_content=final_content,
            mode=result.get("mode", "unknown"),
            blog_kind=plan.blog_kind,
            sections_count=len(plan.tasks),
            word_count=word_count,
        )
        
    except Exception as e:
        return BlogResponse(
            success=False,
            blog_title="",
            blog_content="",
            mode="",
            blog_kind="",
            sections_count=0,
            word_count=0,
            error=str(e)
        )


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    groq_key = os.getenv("GROQ_API_KEY", "")
    return {
        "status": "healthy",
        "groq_configured": groq_key.startswith("gsk_"),
        "tavily_configured": bool(os.getenv("TAVILY_API_KEY"))
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)