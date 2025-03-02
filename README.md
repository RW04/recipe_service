## Recipe AI Service

### Project Overview

The Recipe AI Service is a backend service that enables users to manage ingredient preferences and generate personalized recipes using LLMs. It provides CRUD operations for ingredient preferences and ensures that generated recipes respect user preferences. The project follows modern backend development best practices with FastAPI, Pydantic, and MongoDB.

### Project Structure

```html
📂 Recipe AI Service
├── 📄 .env.example  # Example environment variables file
├── 📄 README.md     # Project documentation
├── 📄 SOLUTIONS.md  # Explanation of approach, design, challenges and future improvements
├── 📄 __init__.py   # Empty file to mark directory as a Python package
├── 📂 app
│   ├── 📄 main.py                     # FastAPI application entry point
│   ├── 📂 api
│   │   ├── 📄 routes.py               # API route definitions
│   ├── 📂 core
│   │   ├── 📄 settings.py             # Configuration settings
│   │   ├── 📄 db_manager.py           # Database setup and session handling
│   ├── 📂 data
│   │   ├── 📄 ingredients_table.csv   # Food Ingredients Dataset
│   ├── 📂 schemas
│   │   ├── 📄 recipe_schema.py        # Pydantic schemas for recipe generation
│   ├── 📂 services
│   │   ├── 📄 recipe_ai.py            # LLM-powered recipe generation
│   ├── 📂 tests
│   │   ├── 📄 test_api.py             # Integration tests for the API
└── 📄 pyproject.toml                  # Dependency management
├── 📄 environment.yml                 # YAML file to install dependencies
```

### Setup Instructions

#### 1. Install Dependencies

Use `pyproject.toml` for dependency management:

```bash
pip install poetry
poetry install
```

Alternatively, create a Conda environment using a `.yml` file:

```bash
conda env create -f environment.yml
conda activate recipe_ai
```

#### 2. Install MongoDB

Install MongoDB 6.0 locally and start the service

```bash 
## Setup Instructions

### macOS:

# Install Homebrew if not installed:  
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install MongoDB
brew tap mongodb/brew 
brew install mongodb-community@6.0

# Start MongoDB
brew services start mongodb-community@6.0

### Linux (Ubuntu/Debian)

# Import MongoDB’s public GPG key and add the repo
curl -fsSL https://www.mongodb.org/static/pgp/server-6.0.asc | sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-6.0.gpg

echo "deb [signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Install MongoDB
sudo apt update
sudo apt install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod

### Windows
# Download MongoDB Community Edition from MongoDB Official Website
# Run the installer and follow the setup wizard.
# Start MongoDB as a service using 
mongod --dbpath <your_db_path>

```

Access MongoDB shell

```bash
mongosh
# Access database
use recipes_db
# Access collection
show collections
# Retrieve entries
db.ingredient_preferences.find().pretty()
```

#### 3. Configure Environment Variables

Copy `.env.example` to `.env` and set appropriate values

```ini
MONGO_URI=mongodb://localhost:27017/
DB_NAME=recipes_db
GITHUB_TOKEN=your-github-token-here
```

### Usage

#### 1. Run the Application

Start the FastAPI service using Uvicorn

```bash
uvicorn app.main:app --reload
```

#### 2. Test API Endpoints

Use `curl`

```bash
curl -X 'POST' 'http://127.0.0.1:8000/generate-recipe/' \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "user1",
    "available_ingredients": ["cauliflower", "onion", "potato", "tomato"],
    "liked_ingredients": ["tomato"],
    "excluded_ingredients": []
  }'
```

Alternatively, visit [Swagger UI](http://localhost:8000/docs) to test the API interactively.

#### 3. CRUD Operations

| **<sub>Endpoint<sub>** | **<sub>Description<sub>** |
|--------------|-----------------|
| <sub>POST /save-preference/</sub> | <sub>Save user ingredient preferences</sub> |
| <sub>GET /get-preference/{user_id}</sub> | <sub>Retrieve user ingredient preferences</sub> |
| <sub>DELETE /delete-preference/{user_id}</sub> | <sub>Delete user ingredient preferences</sub> |
| <sub>POST /generate-recipe/</sub> | <sub>Generate a recipe based on available ingredients</sub> |

#### 4. Sample I/O

```bash
# Sample Input
curl -X 'POST' 'http://127.0.0.1:8000/generate-recipe/' \
-H 'Content-Type: application/json' \
-d '{
"user_id": "user43",
"available_ingredients": ["Potato", "onions", "chicken", "tomato", "garlic"],
"liked_ingredients": ["chicken"],
"excluded_ingredients": ["garlic"]
}'
```

```python
# Sample Output

2025-03-02 07:25:59,181 - INFO - 📌 Received request for recipe generation
2025-03-02 07:25:59,181 - INFO - 📌 Now generating recipe
2025-03-02 07:25:59,182 - INFO - ✅ Database connection confirmed
2025-03-02 07:25:59,182 - INFO - Saving preference for user: user43
2025-03-02 07:25:59,182 - INFO - Creating new preference for user: user43
2025-03-02 07:25:59,183 - INFO - ✅ Preferences saved successfully
2025-03-02 07:25:59,183 - INFO - Available Ingredients: ['potato', 'onion', 'chicken', 'tomato', 'garlic']
2025-03-02 07:25:59,183 - INFO - Liked Ingredients: ['chicken']
2025-03-02 07:25:59,183 - INFO - Excluded Ingredients: ['garlic']
2025-03-02 07:25:59,186 - INFO - Valid Ingredients: ['potato', 'onion', 'chicken', 'tomato', 'garlic']
2025-03-02 07:25:59,186 - INFO - Ingredient Categories: {'protein', 'vegetables'}
2025-03-02 07:25:59,186 - INFO - ✅ Valid Ingredients matched from database: ['potato', 'onion', 'chicken', 'tomato', 'garlic']
2025-03-02 07:25:59,186 - INFO - ✅ Valid Ingredients matched via LLM: []
2025-03-02 07:26:09,138 - INFO - HTTP Request: POST https://models.inference.ai.azure.com/chat/completions "HTTP/1.1 200 OK"
2025-03-02 07:26:09,141 - INFO - Raw LLM Response: 
[
    {
        "title": "Chicken and Potato Bake",
        "ingredients": [
            {"ingredient": "chicken", "quantity": "4 pieces"},
            {"ingredient": "potato", "quantity": "4 medium, sliced"},
            {"ingredient": "onion", "quantity": "1 large, sliced"},
            {"ingredient": "tomato", "quantity": "2, chopped"},
            {"ingredient": "olive oil", "quantity": "2 tablespoons"},
            {"ingredient": "salt", "quantity": "to taste"},
            {"ingredient": "pepper", "quantity": "to taste"}
        ],
        "instructions": [
            "Preheat the oven to 400°F (200°C).",
            "In a baking dish, layer sliced potatoes and onions.",
            "Place the chicken pieces on top.",
            "Add chopped tomatoes over the chicken and season with salt and pepper.",
            "Drizzle olive oil over everything.",
            "Cover with aluminum foil and bake for 30 minutes.",
            "Remove foil and bake for an additional 15-20 minutes until the chicken is cooked through."
        ],
        "estimated_cooking_time": "50 minutes",
        "difficulty_level": "Easy"
    },
    {
        "title": "Tomato and Chicken Stew",
        "ingredients": [
            {"ingredient": "chicken", "quantity": "4 pieces, boneless"},
            {"ingredient": "potato", "quantity": "3 medium, cubed"},
            {"ingredient": "onion", "quantity": "1 large, chopped"},
            {"ingredient": "tomato", "quantity": "4, diced"},
            {"ingredient": "chicken broth", "quantity": "2 cups"},
            {"ingredient": "olive oil", "quantity": "2 tablespoons"},
            {"ingredient": "salt", "quantity": "to taste"},
            {"ingredient": "pepper", "quantity": "to taste"}
        ],
        "instructions": [
            "Heat olive oil in a pot over medium heat.",
            "Sauté chopped onion until translucent.",
            "Add the chicken pieces and sear until browned.",
            "Stir in cubed potatoes and diced tomatoes.",
            "Pour in chicken broth and bring to a simmer.",
            "Cover and cook for about 25-30 minutes until the chicken is cooked and potatoes are tender.",
            "Season with salt and pepper before serving."
        ],
        "estimated_cooking_time": "40 minutes",
        "difficulty_level": "Medium"
    },
    {
        "title": "Chicken and Potato Hash",
        "ingredients": [
            {"ingredient": "chicken", "quantity": "2 cups, cooked and shredded"},
            {"ingredient": "potato", "quantity": "4 medium, diced"},
            {"ingredient": "onion", "quantity": "1 small, diced"},
            {"ingredient": "tomato", "quantity": "1, diced"},
            {"ingredient": "olive oil", "quantity": "3 tablespoons"},
            {"ingredient": "salt", "quantity": "to taste"},
            {"ingredient": "pepper", "quantity": "to taste"}
        ],
        "instructions": [
            "Heat olive oil in a large skillet over medium heat.",
            "Add diced potatoes and cook until browned and tender, about 10-15 minutes.",
            "Stir in the onion and cook until softened.",
            "Add shredded chicken and diced tomato, stir to combine.",
            "Cook for an additional 5-7 minutes until everything is heated through.",
            "Season with salt and pepper before serving."
        ],
        "estimated_cooking_time": "30 minutes",
        "difficulty_level": "Easy"
    },
    {
        "title": "One-Pan Chicken, Potatoes, and Tomatoes",
        "ingredients": [
            {"ingredient": "chicken", "quantity": "4 legs"},
            {"ingredient": "potato", "quantity": "5 medium, quartered"},
            {"ingredient": "onion", "quantity": "2, sliced"},
            {"ingredient": "tomato", "quantity": "3, quartered"},
            {"ingredient": "olive oil", "quantity": "3 tablespoons"},
            {"ingredient": "herbs (such as thyme or rosemary)", "quantity": "1 teaspoon"},
            {"ingredient": "salt", "quantity": "to taste"},
            {"ingredient": "pepper", "quantity": "to taste"}
        ],
        "instructions": [
            "Preheat oven to 425°F (220°C).",
            "In a large roasting pan, combine potatoes, onion, and tomatoes.",
            "Place chicken legs on top and drizzle everything with olive oil.",
            "Sprinkle with herbs, salt, and pepper.",
            "Toss to coat everything evenly.",
            "Roast for 40-50 minutes or until chicken is cooked and golden brown."
        ],
        "estimated_cooking_time": "1 hour",
        "difficulty_level": "Medium"
    },
    {
        "title": "Chicken and Tomato Stuffed Potatoes",
        "ingredients": [
            {"ingredient": "potato", "quantity": "4 large"},
            {"ingredient": "chicken", "quantity": "2 cups, cooked and diced"},
            {"ingredient": "onion", "quantity": "1 small, diced"},
            {"ingredient": "tomato", "quantity": "2, diced"},
            {"ingredient": "olive oil", "quantity": "2 tablespoons"},
            {"ingredient": "cheese (optional)", "quantity": "1 cup, shredded"},
            {"ingredient": "salt", "quantity": "to taste"},
            {"ingredient": "pepper", "quantity": "to taste"}
        ],
        "instructions": [
            "Preheat the oven to 400°F (200°C).",
            "Bake the potatoes for about 40-45 minutes until tender.",
            "In a pan, heat olive oil and sauté the onion until translucent.",
            "Add diced chicken and diced tomatoes, cooking until heated through.",
            "Once potatoes are done, cut them in half and scoop out some of the insides.",
            "Mix the potato insides with the chicken mixture and re-stuff the potatoes.",
            "Top with cheese if desired and bake for an additional 10 minutes."
        ],
        "estimated_cooking_time": "1 hour",
        "difficulty_level": "Medium"
    }
]

2025-03-02 07:26:09,142 - INFO - ✅ Successfully generated 5 recipes
INFO:     127.0.0.1:59546 - "POST /generate-recipe/ HTTP/1.1" 200 OK
```

#### 5. Test the API

This tests whether the API is working as expected.

```bash
python -m pytest app/tests/test_api.py -v
```

---