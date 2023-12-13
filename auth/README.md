# Auth (Sprint 7)

## Getting started

### Building and running for development

**Steps:**

0. Create `.env` file at the project's root directory and fill it with necessary environment variables.
You can find an example of `.env` file in `.env.example`.

1. Build and run docker container with `dev` env:

 ```commandline
./scripts/dev.sh up -d
 ```

2. Activate virtual environment:

 ```commandline
poetry shell
 ```

3. Run `verify_access_token` service locally:

```commandline
uvicorn src.main:app --reload
 ```

or

```commandline
python -m src.main
```

## Running database migrations

NOTE: First run your database inside of docker container

### Apply migrations
```
alembic upgrade head
```

### Create superuser via CLI

To create superuser with all service permissions granted:

```
create-superuser --username superadmin --first-name Jack --last-name Smith
```

## Service documentation

OpenAPI 3 documentation:

- Swagger

    ```
    GET /api/openapi
    ```

- ReDoc

    ```
    GET /redoc
    ```

- OpenAPI json

    ```
    GET /api/openapi.json
    ```

## Service design
### Sequence diagrams
#### Signup
```mermaid
sequenceDiagram
    participant client as Client
    participant verify_access_token as Auth Service
    participant db as SQL Database
    participant rd as In-memory DB
    Note right of client: signup

    client ->>+ verify_access_token: signup POST[username, password, ...]
    verify_access_token ->> verify_access_token: validate input
    verify_access_token ->> verify_access_token: hash(password)

    alt user exists
        verify_access_token ->>+ db: user exists [username]
        db ->>- verify_access_token: False
        verify_access_token ->>- client: 409
    else user does not exist
        verify_access_token ->>+ db: user does not exist [username]
        db ->>- verify_access_token: True
        verify_access_token ->>+ db: create new user [username, hash(passord), ...]
        db ->>- verify_access_token: ok
        verify_access_token ->> client: User(username, ...)
    end
```
#### Signin
```mermaid
sequenceDiagram
    participant client as Client
    participant verify_access_token as Auth Service
    participant db as SQL Database
    participant rd as In-memory DB
    Note right of client: signin

    client ->>+ verify_access_token: signin POST[username, password, ...]
    verify_access_token ->> verify_access_token: validate input
    verify_access_token ->>+ db: get user [username]
    db ->>- verify_access_token: User(username, hash(password), ...)
    verify_access_token ->> verify_access_token: compare passwords

    alt user is valid
        verify_access_token ->> verify_access_token: generate access and refresh tokens
        verify_access_token ->> rd: set(user_id, refresh, <expire>)
        verify_access_token ->> client: access, refresh, User(username, ...)
    else user is not valid
        verify_access_token ->>- client: 401
    end
```
#### Signout
```mermaid
sequenceDiagram
    participant client as Client
    participant verify_access_token as Auth Service
    participant db as SQL Database
    participant rd as In-memory DB
    Note right of client: signout

    client ->>+ verify_access_token: signout POST[] Header[access]
    verify_access_token ->> verify_access_token: verify token
    alt token is valid
        verify_access_token ->> rd: set(access, banned, <expire>)
        verify_access_token ->> rd: set(refresh, banned, <expire>)
        verify_access_token ->> client: 200
    else token is not valid
        verify_access_token ->>- client: 401
    end
```

#### Verify
```mermaid
sequenceDiagram
    participant client as Client
    participant verify_access_token as Auth Service
    participant db as SQL Database
    participant rd as In-memory DB
    Note right of client: verify

    client ->>+ verify_access_token: verify POST[access token]
    verify_access_token ->> verify_access_token: verify token

    alt token is valid
        alt token is not banned
            verify_access_token ->>+ rd: get(access)
            rd ->>+ verify_access_token: None
            verify_access_token ->> client: 200, the same access token
        else token is banned
            verify_access_token ->>+ rd: get(access)
            rd ->>+ verify_access_token: banned
            verify_access_token ->>+ client: 200 {"status": "Provided access token is invalid"}
        end
    else token is not valid
        verify_access_token ->>+ client: 401
    end
```
#### Refresh
```mermaid
sequenceDiagram
    participant client as Client
    participant verify_access_token as Auth Service
    participant db as SQL Database
    participant rd as In-memory DB
    Note right of client: refresh

    client ->>+ verify_access_token: refresh POST[refresh token]
    verify_access_token ->> verify_access_token: verify token

    alt token is valid
        alt token is not banned
            verify_access_token ->>+ rd: get(refresh)
            rd ->>+ verify_access_token: None
            verify_access_token ->> verify_access_token: generate access, refresh token pair
            verify_access_token ->> client: JWTCredentials(access, refresh)
        else token is banned
            verify_access_token ->>+ rd: get(access)
            rd ->>+ verify_access_token: banned
            verify_access_token ->>+ client: 409
        end
    else token is not valid
        verify_access_token ->>+ client: 401
    end
```
#### Get user
```mermaid
sequenceDiagram
    participant client as Client
    participant verify_access_token as Auth Service
    participant db as SQL Database
    participant rd as In-memory DB
    Note right of client: GET USER

    client ->>+ verify_access_token: GET /user HEADER[access]
    verify_access_token ->> verify_access_token: verify token

    alt token is valid
        alt token is not banned
            verify_access_token ->>+ rd: get(access)
            rd ->>+ verify_access_token: None
            verify_access_token ->> verify_access_token: get user_id from a jwt payload part
            verify_access_token ->>+ db: get user(id==user_id)
            db ->>- verify_access_token: User(username, ...)
            verify_access_token ->> client: the serialized User
        else token is banned
            verify_access_token ->>+ rd: get(access)
            rd ->>+ verify_access_token: banned
            verify_access_token ->>+ client: 401
        end
    else token is not valid
        verify_access_token ->>+ client: 401
    end
```
#### Update user
```mermaid
sequenceDiagram
    participant client as Client
    participant verify_access_token as Auth Service
    participant db as SQL Database
    participant rd as In-memory DB
    Note right of client: Update USER

    client ->>+ verify_access_token: PUT[username, ...] /user HEADER[access]
    verify_access_token ->> verify_access_token: verify token
    verify_access_token ->> verify_access_token: validate input data
    alt data is valid:
        alt token is valid
            alt token is not banned
                verify_access_token ->>+ rd: get(access)
                rd ->>+ verify_access_token: None
                verify_access_token ->> verify_access_token: get user_id from a jwt payload part
                verify_access_token ->>+ db: update user(id==user_id).update(username, ...)
                db ->>- verify_access_token: User(username, ...)
                verify_access_token ->> client: the serialized User
            else token is banned
                verify_access_token ->>+ rd: get(access)
                rd ->>+ verify_access_token: banned
                verify_access_token ->>+ client: 401
            end
        else token is not valid
            verify_access_token ->>+ client: 401
        end
    else data is not valid:
        verify_access_token ->>+ client: 422
    end
```
#### Update password
```mermaid
sequenceDiagram
    participant client as Client
    participant verify_access_token as Auth Service
    participant db as SQL Database
    participant rd as In-memory DB
    Note right of client: Update password

    client ->>+ verify_access_token:  /password/change POST[old_pass, pass] HEADER[access]
    verify_access_token ->> verify_access_token: verify token
    verify_access_token ->> verify_access_token: validate input data
    alt data is valid:
        alt token is valid
            alt token is not banned
                verify_access_token ->>+ rd: get(access)
                rd ->>+ verify_access_token: None
                verify_access_token ->> verify_access_token: get user_id from a jwt payload part
                verify_access_token ->>+ db: get user(id==user_id).passsword
                db ->>- verify_access_token: hash(password)
                verify_access_token ->> verify_access_token: check passords(old_pass, password)
                alt hash is valid
                    verify_access_token ->>+ db: update user(id==user_id).update(pass, ...)
                    db ->>- verify_access_token: User(username, ...)
                    verify_access_token ->> client: the serialized User
                else hash is not valid
                    verify_access_token ->>- client: 401
                end
            else token is banned
                verify_access_token ->>+ rd: get(access)
                rd ->>+ verify_access_token: banned
                verify_access_token ->>+ client: 401
            end
        else token is not valid
            verify_access_token ->>+ client: 401
        end
    else data is not valid:
        verify_access_token ->>+ client: 422
    end
```
### Entity diagram
https://dbdiagram.io/d/64a1ad1202bd1c4a5e5f3c99

```
Table users {
  id UUID [primary key]
  username varchar(255)
  password varchar(255)
  first_name varchar(50)
  last_name varchar(50)
  created_at timestamp
  modified_at timestamp

  Indexes {
    (username) [unique]
  }
}

Table roles {
  id UUID [primary key]
  name varchar(50) // superuser, subscriber
  created_at timestamp
  modified_at timestamp

  Indexes {
    (name) [unique]
  }
}

Table users_roles {
  id UUID [primary key]
  user_id UUID
  role_id UUID
  created_at timestamp
  modified_at timestamp

  Indexes {
    (user_id, role_id) [unique]
  }
}

Table permissions {
  id UUID [primary key]
  name varchar(50) // crud_user, comment, like, watch_basic_content, watch_premium_content
  created_at timestamp
  modified_at timestamp

  Indexes {
    (name) [unique]
  }
}

Table roles_permissions {
  id UUID [primary key]
  role_id UUID
  permission_id UUID
  created_at timestamp
  modified_at timestamp

  Indexes {
    (role_id, permission_id) [unique]
  }
}

Table users_login_history {
  id UUID [primary key]
  user_id UUID
  user_agent varchar(255)
  ip_address INET
  created_at timestamp
}

Ref: "users"."id" < "users_roles"."user_id"

Ref: "roles"."id" < "users_roles"."role_id"

Ref: "permissions"."id" < "roles_permissions"."permission_id"

Ref: "roles"."id" < "roles_permissions"."role_id"

Ref: "users"."id" < "users_login_history"."user_id"
```

## Sign in using social accounts

Currently, the service supports sign in using social accounts of the following providers:

- Google
- Yandex

To provide sign in using social accounts, you need to create an application in the developer console of the corresponding provider.

After that, you will receive a `client_id` and a `client_secret`.

- GET `/api/v1/verify_access_token/social/login/{provider_slug}` - redirect to the provider's authorization page.
- GET `/api/v1/verify_access_token/social/verify_access_token/{provider_slug}` - callback url, where the provider will redirect the user after authorization.

_Note: when testing, do not use OpenAPI UI, because it does not support redirects._
