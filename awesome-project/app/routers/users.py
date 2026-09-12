from enum import Enum
from fastapi import (
    Cookie,
    Response,
    Form,
    File,
    UploadFile,
    HTTPException,
    APIRouter,
)
from fastapi.responses import RedirectResponse
from pydantic import (
    BaseModel,
    Field,
    EmailStr,
)
from typing import Annotated, Literal

router = APIRouter()


@router.get("/users/", tags=["users"])
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]


@router.get("/users/me", tags=["users"])
async def read_user_me():
    return {"username": "current_user"}


@router.get("/users/{username}", tags=["users"])
async def read_user(username: str):
    return {"username": username}


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    pass


class UserInDB(UserBase):
    hashed_password: str


def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password


def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    user_id_db = UserInDB(**user_in.model_dump(), hashed_password=hashed_password)
    print("User saved ..not really")
    return user_id_db


class FilterParams(BaseModel):
    model_config = {"extra": "forbid"}

    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []


class User(BaseModel):
    username: str
    full_name: str | None = None


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


data = {
    "isbn-9781529046137": "The Hitchhiker's Guide to the Galaxy",
    "imdb-tt0371724": "The Hitchhiker's Guide to the Galaxy",
    "isbn-9781439512982": "Isaac Asimov: The Complete Stories, Vol. 2",
}


def check_valid_id(id: str):
    if not id.startswith(("isbn-", "imdb-")):
        raise ValueError('Invalid ID format, it must start with "isbn-" or "imdb-"')
    return id


class FormData(BaseModel):
    username: str
    password: str


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


@router.get("/exception_items/{item_id}")
async def read_exception_item(item_id: int):
    if item_id == 3:
        raise HTTPException(status_code=418, detail="Nope, not allowed!")
    return {"item_id": item_id}


@router.get("/unicorns/{name}")
async def read_unicorn(name: str):
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}


@router.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}


@router.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}


@router.post("/login/")
async def login(data: Annotated[FormData, Form()]):
    return data


@router.get("/portal", response_model=None, tags=["portal"])
async def get_portal(teleport: bool = False) -> Response | dict:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com")
    # return JSONResponse(content={"message": "Welcome to the portal!"})
    return {"message": "Welcome to the portal!"}


@router.get("/users/{user_id}/items/{item_id}", tags=["users"])
async def read_user_item_id(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}

    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "This is an amazing item2"})

    return item


@router.get("/cook")
async def cook(key: Annotated[str | None, Cookie()] = None):
    return {"key": key}


@router.get("/models/{model_name}")
async def read_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if "resnet" == ModelName.resnet:
        return {"model_name": model_name, "message": "lecnn all the images tanaka"}

    if model_name.value == ModelName.resnet:
        return {"model_name": model_name, "message": "lecnn all the images tanaka"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "lecnn all the images"}

    return {"model_name": model_name, "message": "have some residuals"}


@router.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


@router.post("/user/")
async def create_user(user: UserIn) -> UserInDB:
    user_saved = fake_save_user(user)

    return user_saved
