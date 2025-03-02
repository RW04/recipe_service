"""
This module contains API tests for the recipe generation service.

It uses pytest and FastAPI's TestClient to test the API endpoints.
"""

from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.services.recipe_ai import generate_recipe

# Initialize the FastAPI test client
client = TestClient(app)

def mock_generate_recipe(request):
    """
    Mock function to simulate AI-generated recipes.

    Returns a list containing a sample recipe with standard structure.
    """
    return [
        {
            "title": "Mocked Recipe 1",
            "ingredients": [
                {"ingredient": "Chicken", "quantity": "1"},
                {"ingredient": "Onion", "quantity": "1"},
                {"ingredient": "Garlic", "quantity": "2 cloves"},
            ],
            "instructions": [
                "Chop the ingredients.",
                "Cook together in a pan.",
                "Serve hot."
            ],
            "estimated_cooking_time": "15 minutes",
            "difficulty_level": "Easy",
        }
    ]

@patch("app.services.recipe_ai.generate_recipe", side_effect=mock_generate_recipe)
def test_generate_recipe(mock_func):
    """
    Test the /generate-recipe/ endpoint with valid input.

    This test mocks the generate_recipe function to ensure the API
    returns a structured response containing recipe details.
    """
    response = client.post(
        "/generate-recipe/",
        json={
            "user_id": "test_user",
            "available_ingredients": ["chicken", "onion", "garlic"],
            "liked_ingredients": ["chicken"],
            "excluded_ingredients": [],
        }
    )

    # Ensure the request was successful
    assert response.status_code == 200

    # Extract response data
    data = response.json()

    # Validate response structure
    assert isinstance(data, list), "Response should be a list of recipes."
    assert len(data) > 0, "At least one recipe should be returned."
    assert "title" in data[0], "Each recipe should have a title."
    assert "ingredients" in data[0], "Each recipe should have ingredients."
    assert "instructions" in data[0], "Each recipe should have instructions."
    assert "estimated_cooking_time" in data[0], "Each recipe should have estimated cooking time."
    assert "difficulty_level" in data[0], "Each recipe should have a difficulty level."
