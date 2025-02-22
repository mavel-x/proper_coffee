from app.api.create_app import create_app
from app.env_settings import Settings

settings = Settings()
app = create_app(settings)
