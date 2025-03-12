from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.routes import upload, github, visualization
from api.middleware import RequestLoggingMiddleware
from config import settings

app = FastAPI(
    title="Code Analyzer",
    description="A tool for analyzing Python projects to visualize dependencies and structure",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(RequestLoggingMiddleware)

# Include routers
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(github.router, prefix="/api/github", tags=["GitHub"])
app.include_router(visualization.router, prefix="/api/visualization", tags=["Visualization"])

@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "Code Analyzer API is running"}

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)