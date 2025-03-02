import os
import logging
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Database connection settings
DATABASE_URL = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "recipes_db")

# Initialize MongoDB client and database
client = AsyncIOMotorClient(DATABASE_URL)
db = client[MONGO_DB_NAME]
preferences_collection = db["ingredient_preferences"]

async def save_preference(user_id: str, liked_ingredients: list, excluded_ingredients: list):
    """
    Save or update user ingredient preferences in the database.

    Args:
        user_id (str): The unique identifier for the user.
        liked_ingredients (list): List of ingredients the user likes.
        excluded_ingredients (list): List of ingredients the user dislikes.

    Raises:
        PyMongoError: If an error occurs during the database operation.
    """
    try:
        logger.info(f"Saving preference for user: {user_id}")
        logger.debug(f"Liked: {liked_ingredients}, Excluded: {excluded_ingredients}")

        existing_preference = await preferences_collection.find_one({"user_id": user_id})
        
        if existing_preference:
            logger.info(f"Updating preference for user: {user_id}")
            await preferences_collection.update_one(
                {"user_id": user_id},
                {"$set": {"liked_ingredients": liked_ingredients, "excluded_ingredients": excluded_ingredients}}
            )
        else:
            logger.info(f"Creating new preference for user: {user_id}")
            await preferences_collection.insert_one({
                "user_id": user_id,
                "liked_ingredients": liked_ingredients,
                "excluded_ingredients": excluded_ingredients
            })
    except PyMongoError as e:
        logger.error(f"Database operation failed: {str(e)}")
        raise  

async def get_preference(user_id: str):
    """
    Retrieve user ingredient preferences from the database.

    Args:
        user_id (str): The unique identifier for the user.

    Returns:
        dict | None: The user's ingredient preferences if found, otherwise None.

    Raises:
        PyMongoError: If an error occurs during the database operation.
        Exception: If an unexpected error occurs.
    """
    try:
        logger.info(f"Retrieving preference for user: {user_id}")
        preference = await preferences_collection.find_one({"user_id": user_id})

        if preference:
            preference["_id"] = str(preference["_id"])
            logger.info(f"Preference found for user: {user_id}")
            return preference
        else:
            logger.info(f"No preference found for user: {user_id}")
            return None

    except PyMongoError as e:
        logger.error(f"Database operation failed: {str(e)}")
        raise  
    except Exception as e:
        logger.error(f"Unexpected error in get_preference: {str(e)}")
        raise  

async def delete_preference(user_id: str):
    """
    Delete user ingredient preferences from the database.

    Args:
        user_id (str): The unique identifier for the user.

    Returns:
        dict: A message indicating the deletion result.

    Raises:
        PyMongoError: If an error occurs during the database operation.
        Exception: If an unexpected error occurs.
    """
    try:
        logger.info(f"Attempting to delete preference for user: {user_id}")

        existing_preference = await preferences_collection.find_one({"user_id": user_id})
        
        if not existing_preference:
            logger.warning(f"No preference found for user: {user_id}")
            return {"message": "No preference found to delete."}

        result = await preferences_collection.delete_one({"user_id": user_id})

        if result.deleted_count > 0:
            logger.info(f"Successfully deleted preference for user: {user_id}")
            return {"message": "Preference deleted successfully."}
        else:
            logger.warning(f"No preference deleted for user: {user_id}")
            return {"message": "No preference was deleted."}

    except PyMongoError as e:
        logger.error(f"Database operation failed: {str(e)}")
        raise  
    except Exception as e:
        logger.error(f"Unexpected error in delete_preference: {str(e)}")
        raise
