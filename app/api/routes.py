from fastapi import APIRouter, HTTPException
from app.schemas.recipe_schema import RecipeRequest, RecipeResponse
from app.services.recipe_ai import generate_recipe
import logging

# Initialize API router
router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
async def root():
    """
    Root endpoint to check if the Recipe AI Service is running.
    
    Returns:
        dict: A message indicating the service status.
    """
    return {"message": "Recipe AI Service is running!"}
