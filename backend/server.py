"""
Bond Guardian API Server
Run with: uvicorn server:app --host 0.0.0.0 --port 8000 --reload
"""

from app.main import app

if __name__ == "__main__":
    import uvicorn
    from app.core.config import settings

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=settings.backend_port,
        reload=settings.debug,
    )
