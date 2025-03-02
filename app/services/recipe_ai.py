import os
import json
import logging
import pandas as pd
from typing import List, Optional
from nltk.stem import WordNetLemmatizer
from openai import OpenAI  # Import OpenAI
from app.schemas.recipe_schema import RecipeRequest, RecipeResponseWithDebug, Ingredient, DebugInfo
from app.core.settings import settings
from app.core.db_manager import save_preference, db

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.getenv("GITHUB_TOKEN")
)

# Load dataset for ingredient categories
DATASET_PATH = "app/data/ingredients_table.csv"
ingredient_df = pd.read_csv(DATASET_PATH)

# Preprocess dataset
ingredient_df["Ingredient"] = ingredient_df["Ingredient"].str.lower().str.replace(" ", "")
ingredient_df["Category"] = ingredient_df["Category"].str.lower().str.replace(" ", "")

# Define core ingredient categories
CORE_CATEGORIES = {"protein", "vegetables", "fruits", "carbs"}

# Initialize WordNet Lemmatizer
lemmatizer = WordNetLemmatizer()


def normalize_ingredient(ingredient: str) -> str:
    """
    Normalizes an ingredient string by converting it to lowercase and lemmatizing it.

    Args:
        ingredient (str): The ingredient string to normalize.

    Returns:
        str: The normalized ingredient string.
    """
    return lemmatizer.lemmatize(ingredient.lower().replace(" ", ""))


def call_llm_for_ingredient(ingredient: str) -> Optional[dict]:
    """
    Calls the LLM to validate and categorize an ingredient if necessary.

    Args:
        ingredient (str): The ingredient to validate and categorize.

    Returns:
        Optional[dict]: A dictionary containing the validation result and category, or None if validation fails.
    """
    try:
        prompt = (
            f"Is '{ingredient}' a food ingredient? Reply only with YES or NO. "
            f"If YES, specify category from {CORE_CATEGORIES}. If none, return 'None'. "
            "Strictly output JSON: {\"valid\": \"YES/NO\", \"category\": \"core_category_or_None\"}."
        )

        response = client.chat.completions.create(
            messages=[{"role": "system", "content": prompt}],
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=20,
            top_p=1
        )

        reply = response.choices[0].message.content.strip()
        logger.info(f"🔍 LLM Raw Response for '{ingredient}': {reply}")

        return json.loads(reply)
    except Exception as e:
        logger.error(f"⚠️ LLM validation failed for '{ingredient}': {e}")
        return None


def is_valid_ingredient(ingredient: str) -> Optional[dict]:
    """
    Checks if an ingredient is valid and gets its category from the database before calling the LLM.

    Args:
        ingredient (str): The ingredient to check.

    Returns:
        Optional[dict]: A dictionary containing the ingredient and its category, or None if the ingredient is invalid.
    """
    normalized_ingredient = normalize_ingredient(ingredient)

    category = get_ingredient_category(normalized_ingredient)
    if category:
        return {"ingredient": normalized_ingredient, "category": category}

    logger.info(f"🔎 Checking '{normalized_ingredient}' in dataset before LLM.")
    llm_result = call_llm_for_ingredient(normalized_ingredient)

    if llm_result and llm_result["valid"].upper() == "YES":
        return {
            "ingredient": normalized_ingredient,
            "category": llm_result["category"] if llm_result["category"] != "None" else None
        }

    return None


def get_ingredient_category(ingredient: str) -> Optional[str]:
    """
    Fetches the category of an ingredient from the dataset.

    Args:
        ingredient (str): The ingredient to lookup.

    Returns:
        Optional[str]: The category of the ingredient, or None if not found.
    """
    category_row = ingredient_df[ingredient_df["Ingredient"] == ingredient]
    return category_row["Category"].values[0] if not category_row.empty else None


async def generate_recipe(request: RecipeRequest) -> list[RecipeResponseWithDebug]:
    """
    Generates recipes based on the provided ingredients and preferences using the LLM.

    Args:
        request (RecipeRequest): The recipe request object containing user preferences and available ingredients.

    Returns:
        list[RecipeResponseWithDebug]: A list of generated recipes with debugging information.
    """
    try:
        await db.command("ping")
        logger.info("✅ Database connection confirmed")

        await save_preference(request.user_id, request.liked_ingredients, request.excluded_ingredients)
        logger.info("✅ Preferences saved successfully")

        # Normalize ingredients
        request.available_ingredients = [normalize_ingredient(ing) for ing in request.available_ingredients]
        request.liked_ingredients = [normalize_ingredient(ing) for ing in request.liked_ingredients]
        request.excluded_ingredients = [normalize_ingredient(ing) for ing in request.excluded_ingredients]

        logger.info(f"Available Ingredients: {request.available_ingredients}")
        logger.info(f"Liked Ingredients: {request.liked_ingredients}")
        logger.info(f"Excluded Ingredients: {request.excluded_ingredients}")

        # Check for conflicting preferences
        conflicting_ingredients = set(request.liked_ingredients) & set(request.excluded_ingredients)
        if conflicting_ingredients:
            error_msg = f"Conflicting preferences detected. These ingredients cannot be both liked and excluded: {', '.join(conflicting_ingredients)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        valid_ingredients = []
        matched_with_database = []
        matched_via_llm = []
        ingredient_categories = set()

        for ing in request.available_ingredients:
            result = is_valid_ingredient(ing)

            if result:
                valid_ingredients.append(result["ingredient"])
                category = result["category"]

                if category:
                    ingredient_categories.add(category)

                if result["ingredient"] in ingredient_df["Ingredient"].values:
                    matched_with_database.append(result["ingredient"])
                else:
                    matched_via_llm.append(result["ingredient"])
            else:
                logger.warning(f"'{ing}' is not recognized as a valid food ingredient.")

        logger.info(f"Valid Ingredients: {valid_ingredients}")
        logger.info(f"Ingredient Categories: {ingredient_categories}")
        logger.info(f"✅ Valid Ingredients matched from database: {matched_with_database}")
        logger.info(f"✅ Valid Ingredients matched via LLM: {matched_via_llm}")

        if len(valid_ingredients) < 3:
            raise ValueError("Not enough valid ingredients. Provide at least 3 food ingredients.")

        if not ingredient_categories.intersection(CORE_CATEGORIES):
            logger.error(f"No core ingredients found. Available categories: {ingredient_categories}")
            raise ValueError("At least one ingredient should be a vegetable, carb, protein, or fruit.")

        prompt = (
            f"Generate up to 5 recipes using these ingredients: {', '.join(valid_ingredients)}. "
            f"Give preference to: {', '.join(request.liked_ingredients)}. "
            f"Exclude: {', '.join(request.excluded_ingredients)}. "
            "Ensure the recipes make culinary sense. "
            "Each recipe must be in JSON format with the following keys: "
            "'title', 'ingredients' (list of objects with 'ingredient' and 'quantity'), "
            "'instructions' (list), 'estimated_cooking_time', 'difficulty_level'. "
            "Return only a valid JSON list, no extra text."
        )

        response = client.chat.completions.create(
            messages=[{"role": "system", "content": prompt}],
            model="gpt-4o-mini",
            temperature=1,
            max_tokens=4096,
            top_p=1
        )
        response_text = response.choices[0].message.content.strip()

        logger.info(f"Raw LLM Response: {response_text}")

        recipes_data = json.loads(response_text.strip("```json").strip("```"))

        return [
            RecipeResponseWithDebug(
                **recipe, debug_info=DebugInfo(
                    matched_with_database=matched_with_database,
                    matched_via_llm=matched_via_llm,
                    raw_llm_response=response_text
                )
            ) for recipe in recipes_data
        ]
    except Exception as e:
        logger.error(f"⚠️ Error generating recipes: {str(e)}")
        raise
