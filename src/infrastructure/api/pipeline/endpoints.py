from fastapi import HTTPException, APIRouter

router = APIRouter(prefix='/pipeline', tags=['pipeline'])


@router.get("/execute")
async def start_pipeline():
    """Start the pipeline."""
    try:
        from src.infrastructure.pipeline import fetching_step, normalization_step, deduplication_step
        fetching_step()
        normalization_step()
        deduplication_step()
        return {"message": "Pipeline executed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing pipeline: {str(e)}")
