from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI

def setup_prometheus(app: FastAPI) -> None:
    Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
    ).instrument(app).expose(app, endpoint="/metrics")