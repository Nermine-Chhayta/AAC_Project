# Loads environment variables from .env using python-dotenv
# and exposes them as simple settings for the rest of the app.

import os
from dotenv import load_dotenv

# Load variables from a .env file in the project root, if present
load_dotenv()

PORT: int = int(os.getenv("PORT", 8000))
APP_ENV: str = os.getenv("APP_ENV", "development")