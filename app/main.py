"""
main.py - Entry point for the Recipe AI Service.

This module sets up a FastAPI application for managing user preferences and generating AI-powered recipes.
It includes:
- Connecting to MongoDB with retries.
- API endpoints for saving, retrieving, and deleting user preferences.
- A recipe generation endpoint using AI.

Author: Amit Kumar
"""

import uvicorn
import logging
import asyncio
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from app.api.routes import router
from app.core.db_manager import save_preference, db, get_preference, delete_preference
from app.schemas.recipe_schema import RecipeRequest
from app.services.recipe_ai import generate_recipe  # Ensure correct import path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for application lifespan.
    - Establishes and verifies a connection to MongoDB.
    - Retries connection up to 3 times if it fails.
    - Ensures proper cleanup when shutting down.
    """
    logger.info("🚀 Starting Recipe AI Service...")
    retries = 3
    while retries > 0:
        try:
            await db.command("ping")  # Check database connection
            logger.info("✅ Successfully connected to MongoDB")
            break
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
            retries -= 1
            if retries == 0:
                raise
            await asyncio.sleep(5)  # Wait before retrying
    yield
    logger.info("🛑 Shutting down Recipe AI Service...")

# Initialize FastAPI application
app = FastAPI(title="Recipe AI Service", lifespan=lifespan)
app.include_router(router)

@app.post("/save-preference/")
async def save_user_preferences(request: RecipeRequest):
    """
    Save user ingredient preferences to the database.
    - Verifies database connection before saving.
    - Logs the process for debugging purposes.
    """
    logging.info("📌 Received request to save preferences")
    logging.debug(f"Request data: {request.dict()}")

    try:
        await db.command("ping")
        logging.info("✅ Database connection confirmed")

        await save_preference(request.user_id, request.liked_ingredients, request.excluded_ingredients)
        logging.info("✅ Preferences saved successfully")

        return {"message": "Preferences saved successfully"}
    except Exception as e:
        logging.error(f"❌ Error in save_user_preferences: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error saving preferences: {str(e)}")

@app.get("/get-preference/{user_id}")
async def get_user_preferences(user_id: str):
    """
    Retrieve user preferences based on user_id.
    - Checks if preferences exist before returning.
    """
    logging.info(f"📌 Received request to get preferences for user: {user_id}")

    try:
        await db.command("ping")
        logging.info("✅ Database connection confirmed")

        preferences = await get_preference(user_id)
        if preferences:
            logging.info("✅ Preferences found and returned")
            return preferences
        else:
            logging.warning("⚠️ No preferences found for this user")
            raise HTTPException(status_code=404, detail="Preferences not found")
    except Exception as e:
        logging.error(f"❌ Error in get_user_preferences: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving preferences: {str(e)}")

@app.delete("/delete-preference/{user_id}")
async def delete_user_preferences(user_id: str):
    """
    Delete user preferences from the database.
    - Checks if preferences exist before attempting deletion.
    """
    logging.info(f"📌 Received request to delete preferences for user: {user_id}")

    try:
        await db.command("ping")
        logging.info("✅ Database connection confirmed")

        response = await delete_preference(user_id)
        if "successfully" in response["message"]:
            logging.info("✅ Preferences deleted successfully")
            return response
        else:
            logging.warning("⚠️ No preferences found to delete")
            raise HTTPException(status_code=404, detail=response["message"])
    except Exception as e:
        logging.error(f"❌ Error in delete_user_preferences: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting preferences: {str(e)}")

@app.post("/generate-recipe/")
async def generate_recipe_endpoint(request: RecipeRequest):
    """
    Generate a recipe based on user preferences and AI.
    - Calls the AI recipe generation function.
    - Returns generated recipes as a response.
    """
    logging.info("📌 Received request for recipe generation")
    logging.debug(f"Request data: {request.dict()}")

    try:
        logging.info("📌 Now generating recipe")
        recipes = await generate_recipe(request)

        logging.info(f"✅ Successfully generated {len(recipes)} recipes")
        return recipes
    except Exception as e:
        logger.error(f"❌ Error in generate_recipe_endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating recipe: {str(e)}")

if __name__ == "__main__":
    """
    Run the FastAPI application using Uvicorn.
    - Sets host to 0.0.0.0 for external accessibility.
    - Enables automatic reload for development.
    """
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
