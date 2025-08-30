# FastAPI App

FastAPI Rest API with [SQLModel](https://sqlmodel.tiangolo.com/) (AsyncSession), JWT and Uvicorn

## Clean Architecture Pattern

router -> service -> repository -> model + schema

## How to Run

```sh
# clone the repo
$ git clone repo

# go into repo's directory
$ cd repo

# copy and edit env file
$ cp .env.example .env

# activated virtual environtment
$ source venv/bin/activate

# run your redis server
$ redis-cli

# migrate db:
$ alembic upgrade head

# seeds data to database
$ python initial_data.py

# run the app
$ python main.py

# list uvicorn (windows)
$ tasklist | findstr uvicorn
# kill uvicorn (windows)
$ taskkill /PID 22396 /F

# run pytest
$ pytest

# run pytest coverage
$ pytest --cov=app --cov-report=html tests/
```

## How to Setup async Alembic SQLModel

```sh
$ alembic init -t async alembic

# import SQLModel into script.py.mako
from alembic import op
import sqlalchemy as sa
import sqlmodel             # NEW
${imports if imports else ""}

# update env.py for db config
from dotenv import load_dotenv  # NEW
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlmodel import SQLModel                       # NEW

from alembic import context
# Import all your models here
from app.models import Hero

load_dotenv()  # NEW

DATABASE_URL = os.getenv("DATABASE_URL")  # NEW
connection_string = f'{DATABASE_URL}'  # NEW

config = context.config
config.set_main_option('sqlalchemy.url', connection_string)  # NEW

...
..
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata             # UPDATED
..
...


# To generate the first migration file, run:
$ alembic revision --autogenerate -m "init"

# To Rolling a Migration Back
$ alembic downgrade -1

# To Apply the migration:
$ alembic upgrade head

```

### Todo List

- [x] FastAPI Log file
- [x] FastAPI Swagger
- [x] Testing with PyTest, Pytest Coverage
- [x] FastAPI Clean Architecture Pattern
  - [x] Routers (handler)
  - [x] Service (usecase - logic process)
  - [x] Repository (process to DB)
  - [x] Error Exception
- [ ] Auth
  - [x] Register, Send verification Email
  - [x] Send Email with [Fastapi-mail](https://sabuhish.github.io/fastapi-mail/) and fastapi BackgroundTasks
  - [x] Open Link Verification Email
  - [x] Resend Verification Email Code
  - [x] Login
  - [x] JWT Auth Middleware + Redis
  - [x] Refresh Token
  - [x] Request Forgot Password, send email with Token
  - [x] Open link Request Forgot Password
  - [x] Submit Request Reset Password
  - [x] Check JWT Blacklist token in Redis
  - [x] Logout + Blacklist token in Redis
- [ ] Account
  - [x] Get Profile (Me)
  - [x] Update Profile
  - [x] Update Photo Profile + center Crop(Square)
  - [ ] Change Password
  - [ ] Deletion Account with email OTP
  - [ ] Recover deleted account (Admin role)
  - [ ] User Activity with interval (last login at, ip address in middleware)
- [x] CRUD
  - [x] Pagination with custom Paginate [FastAPI Pagination](https://uriyyo-fastapi-pagination.netlify.app/)
  - [x] Sort + Search function in List Data
  - [x] Create Data
  - [x] Edit Data
  - [x] Delete Data
- [x] Nested Model Schema
- [ ] Open API with API KEY middleware
- [x] Upload image(compressed/resize)
- [x] Upload Files
- [ ] Remove Files
- [ ] Upload Videos
- [ ] Create thumbnail from videos with ffmpeg

---

## Credits

FastAPI Tutorial  
https://fastapi.tiangolo.com/tutorial/

Structure FastAPI Projects - How to Structure Your FastAPI Projects  
https://medium.com/@amirm.lavasani/how-to-structure-your-fastapi-projects-0219a6600a8f

FastAPI with Async SQLAlchemy, SQLModel, and Alembic  
https://testdriven.io/blog/fastapi-sqlmodel/

FastAPI Best Practices and Design Patterns: Building Quality Python APIs  
https://medium.com/@lautisuarez081/fastapi-best-practices-and-design-patterns-building-quality-python-apis-31774ff3c28a

Generic Repository in FastApi that is managing relationships - PART 1  
https://dev.to/messanga11/generic-repository-in-fastapi-that-is-managing-relationships-part-1-1k40

Structuring FastAPI Project Using 3-Tier Design Pattern - fastapi-services-oauth2 -> (Used for service and repo)  
https://levelup.gitconnected.com/structuring-fastapi-project-using-3-tier-design-pattern-4d2e88a55757  
https://github.com/viktorsapozhok/fastapi-services-oauth2

FastAPI Beyond CRUD -> (Used for JWT)
https://www.youtube.com/watch?v=Uw4FPr-dD7Q&list=PLEt8Tae2spYnHy378vMlPH--87cfeh33P  
https://github.com/jod35/fastapi-beyond-CRUD/tree/main

How To Customize Default JSON Response Class in FastAPI  
https://mohsen-khodabakhshi.medium.com/customize-response-class-fastapi-83be3b32aa39

Async configuration for FastAPI and SQLModel  
https://github.com/jonra1993/fastapi-alembic-sqlmodel-async/tree/main

Setting up a FastAPI App with Async SQLALchemy 2.0 & Pydantic V2  
https://medium.com/@tclaitken/setting-up-a-fastapi-app-with-async-sqlalchemy-2-0-pydantic-v2-e6c540be4308

Canvas' Transactional Email Templates  
https://github.com/usecanvas/email-templates/tree/master
