import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from src.config import settings

if __name__ == "__main__":
    print(f"Starting server on {settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run(
        "src.api.server:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
