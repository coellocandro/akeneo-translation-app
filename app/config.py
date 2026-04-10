import os

class Settings:
    app_url = os.getenv("APP_URL", "http://localhost:8000")

    akeneo_url = os.getenv("AKENEO_URL", "http://localhost:8080")
    akeneo_client_id = os.getenv("AKENEO_CLIENT_ID", "")
    akeneo_client_secret = os.getenv("AKENEO_CLIENT_SECRET", "")
    akeneo_username = os.getenv("AKENEO_USERNAME", "")
    akeneo_password = os.getenv("AKENEO_PASSWORD", "")

    libretranslate_url = os.getenv("LIBRETRANSLATE_URL", "http://localhost:5000")

settings = Settings()
