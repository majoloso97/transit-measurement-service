import uvicorn
from fastapi import FastAPI
from settings import settings
from api.routes.v1 import welcome
from api.routes.v1 import checks


app = FastAPI(title="Service for video processing in transit measurment app",
              description="This is a REST API for interacting \
                with the video processing service. \
                It uses FastAPI as the web framework and YOLO \
                model for ML operations.")

app.include_router(welcome.router)
app.include_router(checks.router)

if __name__ == "__main__":
    uvicorn.run("main:app",
                host="0.0.0.0",
                port=80,
                reload=settings.AUTO_RELOAD)
