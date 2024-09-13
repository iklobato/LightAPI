---
title: Databse
---

## Databases Compatibility

LightAPI supports the following databases:

-   SQLite
-   PostgreSQL
-   MySQL
-   MariaDB
-   Oracle
-   MS-SQL

## Connecting to a Database

Set the `DATABASE_URL` environment variable to connect to your database:

``` py
import os os.environ['DATABASE_URL'] = "postgresql://user:password@postgresserver/db"
```

If no `DATABASE_URL` is provided, LightAPI defaults to using an in-memory SQLite database.

## API Endpoints

LightAPI automatically generates the following endpoints for each model, the endpoint name is based on the class name:

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