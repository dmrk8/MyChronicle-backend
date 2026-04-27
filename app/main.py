from app.core.config import get_settings
from app.core.factory import create_app

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

from app.observability.setup import setup_telemetry


# setup_telemetry(get_settings())

app = create_app(get_settings())

FastAPIInstrumentor().instrument_app(app)
HTTPXClientInstrumentor().instrument()
