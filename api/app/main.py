from app.dependencies import get_settings
from app.setup_app import get_application

settings = get_settings()
app = get_application(settings)
