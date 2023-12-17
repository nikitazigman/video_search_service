# Stream API

## How to start 
1. Create `.env` file based on the `.env.example`.
2. Run the main docker compose `dev.yaml` file: 
    ``` bash
    # in the root dir 
    ./scripts/dev.sh up -d
    ```
3. Activate `poetry` virtual env:
    ```
    cd stream_api/
    poetry shell
    poetry install
    ```
4. Run `Stream API` service:
    ``` bash
    # under the poetry virtual env
    python -m stream_api.main
    ```
5. Run `auth` service following [the documentation](../auth/README.md).

6. Run `cdn_api` service following [the documentation](../cdn_api/README.md).


## Service documentation

OpenAPI 3 documentation:

- Swagger
    ```
    GET /docs
    ```

- ReDoc
    ```
    GET /redoc
    ```

- OpenAPI json
    ```
    GET /docs/openapi.json
    ```
