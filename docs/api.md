---
title: API Endpoints
---

LightAPI automatically generates the following endpoints for each model:

| HTTP Method | Endpoint Example            | Handler Class          | Description                                              |
|-------------|-----------------------------|------------------------|----------------------------------------------------------|
| POST        | `/person/`                  | CreateHandler          | Creates a new item in the `person` model                 |
| GET         | `/person/`                  | RetrieveAllHandler     | Retrieves all items from the `person` model              |
| GET         | `/person/{id}`              | ReadHandler            | Retrieves a specific item by ID from the `person` model  |
| PUT         | `/person/{id}`              | UpdateHandler          | Updates an existing item by ID in the `person` model     |
| PATCH       | `/person/{id}`              | PatchHandler           | Partially updates an existing item by ID in the `person` model |
| DELETE      | `/person/{id}`              | DeleteHandler          | Deletes an existing item by ID in the `person` model     |
| OPTIONS     | `/person/`                  | OptionsHandler         | Returns allowed HTTP methods and headers for the `person` model |
| HEAD        | `/person/`                  | HeadHandler            | Returns response headers only for the `person` model     |