import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """
    Application settings loaded from environment variables.
    """
    PROJECT_NAME: str = "Recipe AI Service"
    MONGO_URI: str = os.getenv("MONGO_URI")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME")
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN")
    API_KEY: str = os.getenv("API_KEY", "your_default_api_key")  # Default API key for authentication

    def __init__(self):
        """
        Ensures that essential configurations are properly loaded.
        
        Raises:
            ValueError: If required environment variables are missing.
        """
        missing_vars = []
        if not self.MONGO_URI:
            missing_vars.append("MONGO_URI")
        if not self.MONGO_DB_NAME:
            missing_vars.append("MONGO_DB_NAME")
        if not self.GITHUB_TOKEN:
            missing_vars.append("GITHUB_TOKEN")

        if missing_vars:
            raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")

# Create a singleton instance of Settings for the app
settings = Settings()
