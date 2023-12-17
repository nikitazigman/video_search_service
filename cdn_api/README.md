# CDN API

## How to start

1. Create `.env` file based on the `.env.example`.

   _Note: Sign in to `minio` console and create access keys `http://localhost:9090/access-keys` and then put them to `MINIO_ACCESS_KEY` and
   `MINIO_SECRET_KEY` envs._

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
4. Run `CDN API` service:
    ``` bash
    # under the poetry virtual env
    python -m cdn_api.main
    ```

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
