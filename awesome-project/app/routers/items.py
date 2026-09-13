from enum import Enum
from fastapi import (
    Body,
    Cookie,
    Response,
    status,
    File,
    UploadFile,
    HTTPException,
    APIRouter,
    Path,
    Query,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse
from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
)
from typing import Annotated, Literal

router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)

fake_db = {}


class BaseItem(BaseModel):
    description: str
    type: str


class CartItem(BaseItem):
    type: str = "car"


class PlaneItem(BaseItem):
    type: str = "plane"
    size: int


plane_cart_items = {
    "item1": {"description": "A car item", "type": "car"},
    "item2": {"description": "A plane item", "type": "plane", "size": 10},
}


def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password


class FilterParams(BaseModel):
    model_config = {"extra": "forbid"}

    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str = Field(examples=["Foo"])
    description: str | None = Field(
        default=None, examples=["A very nice item"], title="title item", max_length=100
    )
    price: float = Field(
        gt=10,
        description="desc item",
        examples=[42.0],
    )
    tax: float | None = Field(default=None, examples=[3.2])
    tags: set[str] = set()
    images: list[Image] | None = None

    # model_config = {
    #     "json_schema_extra": {
    #         "examples": [
    #             {
    #                 "name": "Foo",
    #                 "description": "A very nice item",
    #                 "price": 42.0,
    #                 "tax": 3.2,
    #             }
    #         ]
    #     }
    # }


class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item]


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


fake_items_db = [
    {"item_name": "Foo"},
    {"item_name": "Bar"},
    {"item_name": "Baz"},
    {"item_name": "Foo1"},
    {"item_name": "Bar1"},
    {"item_name": "Baz1"},
]

items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}

data = {
    "isbn-9781529046137": "The Hitchhiker's Guide to the Galaxy",
    "imdb-tt0371724": "The Hitchhiker's Guide to the Galaxy",
    "isbn-9781439512982": "Isaac Asimov: The Complete Stories, Vol. 2",
}


def check_valid_id(id: str):
    if not id.startswith(("isbn-", "imdb-")):
        raise ValueError('Invalid ID format, it must start with "isbn-" or "imdb-"')
    return id


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


@router.get("/exception/{item_id}")
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


@router.get("/portal", response_model=None, tags=["portal"])
async def get_portal(teleport: bool = False) -> Response | dict:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com")
    # return JSONResponse(content={"message": "Welcome to the portal!"})
    return {"message": "Welcome to the portal!"}


@router.get("/pydantic_items/")
async def read_pydantic_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query


@router.get("/cook")
async def cook(key: Annotated[str | None, Cookie()] = None):
    return {"key": key}


@router.get(
    "/response/{item_id}/name",
    response_model=Item,
    response_model_include={"name", "description"},
)
async def read_item_name(item_id: str):
    return items[item_id]


@router.get(
    "/response/{item_id}/public",
    response_model=Item,
    response_model_exclude={"tax"},
)
async def read_item_public_data(item_id: str):
    return items[item_id]


@router.get(
    "/response/{item_id}", response_model=Item, response_model_exclude_unset=False
)
async def read_response_item(item_id: str):
    res_item = items[item_id]
    print(res_item)
    return res_item


@router.get("/{item_id}")
async def read_item(
    *,
    needy: Annotated[str | None, Query(alias="needy")] = None,
    item_id: Annotated[int, Path(title="The ID of the item", gt=0, le=100)],
    skip: int = 0,
    limit: int | None = None,
):
    results = {"item_id": item_id, "needy": needy, "skip": skip, "limit": limit}

    if needy:
        results.update({"needy": needy})

    return results


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


@router.post("/offers/")
async def create_offer(offer: Offer):
    return offer


@router.post("/images/multiple/")
async def create_multiple_images(images: list[Image]):
    return images


@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: Item) -> Item:
    """
    サンプルのコメント
    - ここにMarkdownでコメントが
    - 書けるらしい
    """
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item


@router.get("/plane_cart/{item_id}", response_model=PlaneItem | CartItem)
async def read_plane_cart(item_id: str):
    return plane_cart_items[item_id]


@router.put(
    "/{item_id}",
    tags=["custom"],
    responses={403: {"description": "Operation forbidden"}},
)
async def update_item(
    *,
    item_id: Annotated[int, Path(title="The ID of the item", gt=0, le=100)],
    q: str | None = None,
    # item: Item,
    # item: Annotated[Item, Body(embed=True)],
    item: Annotated[
        Item,
        Body(
            # examples=[
            #     {
            #         "name": "Foo",
            #         "description": "A very nice item",
            #         "price": 42.0,
            #         "tax": 3.2,
            #     },
            #     {
            #         "name": "Bar",
            #         "description": "Another item",
            #         "price": 35.4,
            #     },
            # ],
            openapi_examples={
                "normal": {
                    "summary": "A normal example",
                    "description": "A **normal** item works correctly.",
                    "value": {
                        "name": "Foo",
                        "description": "A very nice Item",
                        "price": 35.4,
                        "tax": 3.2,
                    },
                },
                "converted": {
                    "summary": "An example with converted data",
                    "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                    "value": {
                        "name": "Bar",
                        "price": "35.4",
                    },
                },
                "invalid": {
                    "summary": "Invalid data is rejected with an error",
                    "value": {
                        "name": "Baz",
                        "price": "thirty five point four",
                    },
                },
            },
        ),
    ],
    importance: Annotated[int, Body(gt=20)],
):
    result = {"item_id": item_id, "item": item, "importance": importance}

    if q:
        result.update({"q": q})

    return result


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


@router.put("/jsonable/{id}", response_model=Item)
def update_jsonable(id: str, item: Item):
    update_item_encoded = jsonable_encoder(item)
    items[id] = update_item_encoded

    return update_item_encoded
    # fake_db[id] = json_compatible_item_data
