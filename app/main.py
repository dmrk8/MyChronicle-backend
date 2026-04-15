from app.core.config import get_settings
from app.core.factory import create_app

app = create_app(get_settings())
