# CDN service

**[Link to the project to be reviewed](https://github.com/alena-kono/graduate_work)**

## Components
### Auth service
Check the documentation [here](auth/README.md).

### CDN API service
Check the documentation [here](cdn_api/README.md).

### Video Converter service
Check the documentation [here](video_converter/README.md).

### Stream API service
Check the documentation [here](stream_api/README.md).

## Service ports mappings for the local development
0. `auth`: port 8001
1. `cdn_api`: port 8002
2. `stream_api`: port 8003

## HOW TO

### HOW TO START

1. Run `dev` docker compose:
    ```
    sh ./scripts/dev.sh up
    ```

2. Set up each service following docs from [this section](#components).

### HOW TO USE

1. Create user with superuser privileges following [the docs](auth/README.md#create-superuser-via-cli).
2. Sign in at `Auth` service to get JWT credentials. Save access JWT, you will need it later.
   ```
   curl --location 'http://localhost:8001/api/v1/auth/signin' \
   --header 'Content-Type: application/x-www-form-urlencoded' \
   --data-urlencode 'username=superuser' \
   --data-urlencode 'password=Qwerty123'
   ```
3. Upload video via `CDN API` service. Save `id` of a task to check its status later.
   ```
   curl --location 'http://localhost:8002/api/v1/upload?video_id=c1efb7fe-d8a1-45ee-b939-e7c4df8cd666' \
   --form 'file=@"/Users/superuser-name/short_movie.mp4"'
   ```
4. The video upload and processing has been started. Check the status via `CDN API` service:
   ```
   curl --location 'http://localhost:8002/api/v1/tasks/119a5b2e-990e-4ae8-b666-aedacde78bc5'
   ```
   Once the status is `done`, go to the next step.
5. Get a video manifest file (.m3u8) via `Stream API` using your access token:
   ```
   curl --location 'http://localhost:8003/api/v1/hls/manifest/c1efb7fe-d8a1-45ee-b939-e7c4df8cd666' \
   --header 'Authorization: ACCESS_TOKEN'
   ```
