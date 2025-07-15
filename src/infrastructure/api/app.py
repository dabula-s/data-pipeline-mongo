from fastapi import FastAPI

from src.infrastructure.api.pipeline.endpoints import router as pipeline_router
from src.infrastructure.api.plots.endpoints import router as plots_router

app = FastAPI()

app.include_router(pipeline_router)
app.include_router(plots_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
