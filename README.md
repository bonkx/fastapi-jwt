# FastAPI App

FastAPI Rest API with [SQLModel](https://sqlmodel.tiangolo.com/) (AsyncSession) and Uvicorn


## Clean Architecture Pattern
router -> service -> repository -> model

## How to Run

```bash
# clone the repo
$ git clone repo

# go into repo's directory
$ cd repo

# copy and edit env file
$ cp .env.example .env

# seeds data to database like status
$ db migrate

# build docker
$ make build

# start docker
$ make run
```

### Todo List

- [x] FastAPI Log file, Favicon
- [x] FastAPI Swagger
- [x] FastAPI Clean Architecture Pattern
  - [x] Routers (controller)
  - [x] Service (usecase - logic process)
  - [x] Repository (process to DB)
  - [x] Error Exception
- [] Auth
  - [] Register, Send verification Email
  - [] Send Email with [Fastapi-mail](https://sabuhish.github.io/fastapi-mail/)
  - [] Open Link Verification Email
  - [] Resend Verification Email Code
  - [] Login
  - [] JWT Auth Middleware + Redis
  - [] Refresh Token
  - [] Forgot Password, send email OTP
  - [] Forgot Password Verify OTP
  - [] Reset Password
  - [] Logout
- [] Account
  - [] Get Profile
  - [] Update Profile
  - [] Update Photo Profile + thumbnail
  - [] Upload File, upload image(compressed)
  - [] Change Password
  - [] Deletion Account with OTP
  - [] Recover deleted account (Admin role)
  - [] User Activity with interval (last login at, ip address in middleware)
- [] CRUD
  - [x] Pagination with custom Paginate [FastAPI Pagination](https://uriyyo-fastapi-pagination.netlify.app/)
  - [x] Sort + Search function in List Data
  - [x] Create Data
  - [] Edit Data
  - [] Delete Data
- [] Preload Model (Associations Struct)
- [] Struct MarshalJSON (Custom representation)
- [] Open API with API KEY middleware
- [] Upload Files
- [] Remove Files
- [] Upload Videos
- [] Create thumbnail from videos with ffmpeg
- [] Upload Images and Compress Image with libvips
- [] Create thumbnail from image
- [] Image Processing with [libvips](https://www.libvips.org/)

---


### [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
### [Structure FastAPI Projects - How to Structure Your FastAPI Projects](https://medium.com/@amirm.lavasani/how-to-structure-your-fastapi-projects-0219a6600a8f)

FastAPI Best Practices and Design Patterns: Building Quality Python APIs
https://medium.com/@lautisuarez081/fastapi-best-practices-and-design-patterns-building-quality-python-apis-31774ff3c28a

Generic Repository in FastApi that is managing relationships - PART 1
https://dev.to/messanga11/generic-repository-in-fastapi-that-is-managing-relationships-part-1-1k40 

Structuring FastAPI Project Using 3-Tier Design Pattern - fastapi-services-oauth2 (Used for service and repo)
https://levelup.gitconnected.com/structuring-fastapi-project-using-3-tier-design-pattern-4d2e88a55757
https://github.com/viktorsapozhok/fastapi-services-oauth2

How To Customize Default JSON Response Class in FastAPI
https://mohsen-khodabakhshi.medium.com/customize-response-class-fastapi-83be3b32aa39

FastAPI Beyond CRUD
https://www.youtube.com/watch?v=Uw4FPr-dD7Q&list=PLEt8Tae2spYnHy378vMlPH--87cfeh33P
https://github.com/jod35/fastapi-beyond-CRUD/tree/main

Async configuration for FastAPI and SQLModel
https://github.com/jonra1993/fastapi-alembic-sqlmodel-async/tree/main

Setting up a FastAPI App with Async SQLALchemy 2.0 & Pydantic V2
https://medium.com/@tclaitken/setting-up-a-fastapi-app-with-async-sqlalchemy-2-0-pydantic-v2-e6c540be4308