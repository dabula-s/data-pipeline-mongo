from fastapi import HTTPException, Depends, APIRouter
from fastapi.responses import StreamingResponse

from src.core.ports.repositories import HostNormalizedDataRepository
from src.infrastructure.api.dependencies import get_normal_repository
from src.infrastructure.api.utils import create_bar_plot, create_pie_plot, create_stacked_bar_plot
from src.settings import PLOTS_SOURCE_COLLECTION

router = APIRouter(prefix='/plots', tags=['plots'])


@router.get("/os-distribution", response_class=StreamingResponse)
async def get_os_distribution_plot(repo: HostNormalizedDataRepository = Depends(get_normal_repository)):
    """Return a bar plot of the operating system distribution."""
    try:
        data = await repo.get_os_distribution(collection=PLOTS_SOURCE_COLLECTION)
        if not data:
            raise HTTPException(status_code=404, detail="No data available for OS distribution")

        buffer = create_bar_plot(
            data=data,
            title="Host Distribution by Operating System",
            x_label="Operating System",
            y_label="Number of Hosts"
        )
        return StreamingResponse(buffer, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating plot: {str(e)}")


@router.get("/old-vs-new-hosts", response_class=StreamingResponse)
async def get_old_vs_new_hosts_plot(
        days_threshold: int = 30,
        repo: HostNormalizedDataRepository = Depends(get_normal_repository),
):
    """Return a pie chart of old vs new hosts."""
    try:
        data = await repo.get_old_vs_new_hosts(collection=PLOTS_SOURCE_COLLECTION, days_threshold=days_threshold)
        if not data or sum(data.values()) == 0:
            raise HTTPException(status_code=404, detail="No data available for old vs new hosts")

        buffer = create_pie_plot(
            data=data,
            title=f"Old vs New Hosts (Threshold: {days_threshold} days)"
        )
        return StreamingResponse(buffer, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating plot: {str(e)}")


@router.get("/open-ports-distribution", response_class=StreamingResponse)
async def get_open_ports_distribution_plot(repo: HostNormalizedDataRepository = Depends(get_normal_repository)):
    """Return a bar plot of the open ports distribution."""
    try:
        data = await repo.get_open_ports_distribution(collection=PLOTS_SOURCE_COLLECTION)
        if not data:
            raise HTTPException(status_code=404, detail="No data available for open ports distribution")

        buffer = create_bar_plot(
            data=data,
            title="Open Ports Distribution",
            x_label="Port Number",
            y_label="Frequency"
        )
        return StreamingResponse(buffer, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating plot: {str(e)}")


@router.get("/open-ports-by-platform-distribution", response_class=StreamingResponse)
async def get_open_ports_by_platform_distribution_plot(
        ports: str = "80,443",
        repo: HostNormalizedDataRepository = Depends(get_normal_repository),
):
    try:
        port_list = [int(p) for p in ports.split(",") if p.strip().isdigit()]
        if not port_list:
            raise HTTPException(status_code=400, detail="Invalid or empty ports list")
        data = await repo.get_open_ports_by_platform_distribution(collection=PLOTS_SOURCE_COLLECTION,
                                                                  ports_list=port_list)
        if not data:
            raise HTTPException(status_code=404, detail="No data available for open ports by platform")
        buffer = create_stacked_bar_plot(
            data=data,
            ports=port_list,
            title=f"Open Ports by Platform (Ports: {', '.join(map(str, port_list))})",
            x_label="Platform",
            y_label="Number of Hosts"
        )
        return StreamingResponse(buffer, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating plot: {str(e)}")
