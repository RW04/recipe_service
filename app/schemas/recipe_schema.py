from pydantic import BaseModel, field_validator, ValidationInfo
from typing import List, Optional

class Ingredient(BaseModel):
    """
    Represents an ingredient with its name and quantity.
    """
    ingredient: str
    quantity: str  

class RecipeRequest(BaseModel):
    """
    Request schema for generating a recipe based on user preferences.
    """
    user_id: str
    available_ingredients: List[str]
    liked_ingredients: Optional[List[str]] = None
    excluded_ingredients: Optional[List[str]] = None

    @field_validator("liked_ingredients", "excluded_ingredients", mode="before")
    @classmethod
    def default_empty_list(cls, ingredients):
        """
        Ensures that liked_ingredients and excluded_ingredients default to an empty list if not provided.
        """
        return ingredients if ingredients is not None else []

    @field_validator("liked_ingredients", "excluded_ingredients", mode="before")
    @classmethod
    def validate_ingredients(cls, ingredients: List[str], info: ValidationInfo):
        """
        Validates that liked and excluded ingredients are present in the available ingredients list.
        
        Args:
            ingredients (List[str]): List of ingredients to validate.
            info (ValidationInfo): Validation information containing request data.
        
        Raises:
            ValueError: If an ingredient is not found in the available_ingredients list.
        """
        available = info.data.get("available_ingredients", [])
        if not isinstance(ingredients, list):
            raise ValueError("Ingredients must be a list")
        for ingredient in ingredients:
            if ingredient.lower() not in [a.lower() for a in available]:
                raise ValueError(f"'{ingredient}' must be in available_ingredients")
        return ingredients

class RecipeResponse(BaseModel):
    """
    Response schema for a generated recipe.
    """
    title: str
    ingredients: List[Ingredient]
    instructions: List[str]  # List of step-by-step instructions
    estimated_cooking_time: str  # Example: "20 minutes"
    difficulty_level: str  # Example: "Easy", "Medium", "Hard"

class DebugInfo(BaseModel):
    """
    Debugging details for recipe generation, capturing ingredient matching and raw LLM responses.
    """
    matched_with_database: List[str]
    matched_via_llm: List[str]
    final_liked_ingredients: List[str] = []
    final_excluded_ingredients: List[str] = []
    raw_llm_response: str  # Stores raw LLM response for debugging purposes

class RecipeResponseWithDebug(RecipeResponse):
    """
    Extended recipe response including debug information.
    """
    debug_info: DebugInfo
