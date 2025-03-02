## Overview

This document provides an overview of the design choices, challenges, and future improvements of the Recipe AI Service.

## Key Design Decisions

#### 1. MongoDB as Database

- Schema flexibility allows efficient storage of user preferences.

- Document-oriented design fits well with hierarchical recipe structures.

#### 2. Data Source

- A dataset `ingredients_table.csv` is curated using the ingredients list from [Hugging Face Food Ingredients Dataset](https://huggingface.co/datasets/Scuccorese/food-ingredients-dataset) to categorize common ingredients, reducing unnecessary LLM calls.

- Augmented dataset with additional ingredients to cover more scenarios.

#### 3. Ingredient Categorization

- Ingredients are classified into `vegetables`, `carbs`, `protein`, `fruits`, `oils`, `sugars`, `salts`, `condiments`, `seasonings`

- If an ingredient is missing from the dataset, LLM verifies if it is a valid food ingredient and if it belongs to one of the core categories before recipe generation.

#### 4. Recipe Generation Logic

- Recipes require at least **3 ingredients**, with at least one from core categories (vegetable, carb, protein, fruit).

- Uses LLM prompt to generate structured JSON output of recipes with a list of `ingredients`, `quantities`, `estimated cooking time`, and `difficulty level`.

#### 5. User-Friendly Preference Selection

- Users input `available ingredients` and can optionally specify `liked/excluded` ingredients.

- Avoids forcing users to categorize every ingredient manually.

#### 6. Quality Assurance Mechanism

- Validates response structure.
- Ensures disliked ingredients are excluded.
- Handles edge cases such as conflicting preferences.

## Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| Handling unknown ingredients | First check database, then use LLM to validate food ingredients |
| Reducing LLM API calls | Prebuilt dataset for common ingredients minimizes redundant LLM queries |
| Ensuring valid recipes | Recipes require at least one ingredient from core categories |
| Conflicting preferences | If `liked_ingredients` and `excluded_ingredients` overlap, reject the request |

## Example API Requests and Expected Outcomes

| Available Ingredients                                      | Liked        | Excluded     | Valid for Recipe Generation? | Reason                                                                                                                                           |
| :--------------------------------------------------------- | :----------- | :----------- | :----- | :----------------------------------------------------------------------------------------------------------------------------------------------- |
| `["quinoa", "mango", "kale"]`                             | `["mango"]`  | `[]`         | ✅     | Minimum 3 ingredients in the `available_ingredients` list with at least one of them belonging to core category.        |
| `["sugar", "soy sauce", "salt"]`                           | `["salt"]`   | `[]`         | ❌     | Minimum 3 ingredients in the `available_ingredients` list with none of them belonging to any of the core categories.           |
| `["cauliflower", "onion", "potato", "tomato"]`             | `["egg plants"]` | `[]`         | ❌     | Ingredient in    `liked_ingredient` is not part of `available_ingredients` list.                                   |
| `["cauliflower", "onion", "potato", "tomato"]`             | `[]`         | `["egg plants"]` | ❌     | Ingredient in `excluded_ingredient` is not part of `available_ingredients` list.                 |
| `["cauliflower", "onion", "potato", "tomato"]`             | `[]`         | `[]`         | ✅     | `liked_ingredient`and  `excluded_ingredient` lists are optional ingredients mentioned in `available_ingredients` list are valid and at least one of them belongs to one of the core categories.                |
| `["cauliflower", "onion", "potato", "tomato"]`             | `["onion"]`  | `["onion"]`  | ❌     | Conflicting preferences                 |
| `["Potato", "onions", "chicken", "tomato", "garlic"]`       | `["chicken"]`  | `["garlic"]` | ✅     | Ingredients listed in available_ingredients are case-insensitive and can be in singular or plural form, as the system uses normalized ingredient names for matching. |
| `["okra", "beans", "chair"]`                               | `["okra"]`   | `[]`         | ❌     |  Input contains exactly three ingredients, and one of these ingredients is non-food item.                              |
| `["okra", "beans", "chair", "spinach", "truck"]`           | `["okra"]`   | `[]`         | ✅     | Input contains 3 valid food ingredients with at least one of them belongs to core category, non-food ingredient is discarded                      |

<br>

## Future Improvements

1. **Use MongoDB Atlas Instead of Localhost**
   - A production system requires a secure and scalable database. Using MongoDB Atlas ensures encrypted, managed, and globally distributed databases with automatic backups.

2. **Handling Concurrent Users (Scaling)**
   - If 100+ users access the system at the same time, the following strategies can be applied:
     - **Database Optimization**: Indexing and query optimization for fast lookups.
     - **Connection Pooling**: Use `motor` (async MongoDB driver) with a connection pool.
     - **Load Balancing**: Deploy API using **FastAPI with Gunicorn + Uvicorn workers**.
     - **Asynchronous Task Queue**: Move intensive recipe generation to Celery workers with Redis as a task queue.
     - **Caching**: Use Redis to store frequently accessed recipes and ingredient data to reduce API calls to the LLM.
     - **Autoscaling**: Deploy on **AWS Lambda or Kubernetes** for automatic horizontal scaling.

3. **Auto-Updating the Ingredient Database**
   - Whenever an ingredient is classified as a valid food item by LLM, store it in the database.
   - Next time someone queries the same ingredient, we fetch from the DB instead of calling the LLM thereby lowering cost (by reducing LLM calls), speeds up ingredient validation (faster response time) and automatically grows the database with real-world user input.

---
