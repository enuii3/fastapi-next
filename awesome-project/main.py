from enum import Enum
from fastapi import FastAPI, Body, Cookie, Response
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    EmailStr,
    AfterValidator,
)
from typing import Annotated, Literal
from fastapi import FastAPI, Query, Path
import random


class BaseUser(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


class UserIn(BaseUser):
    password: str


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


class User(BaseModel):
    username: str
    full_name: str | None = None


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


app = FastAPI()


@app.get("/portal", response_model=None)
async def get_portal(teleport: bool = False) -> Response | dict:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com")
    # return JSONResponse(content={"message": "Welcome to the portal!"})
    return {"message": "Welcome to the portal!"}


@app.get("/pydantic_items/")
async def read_pydantic_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query


@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item_id(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}

    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "This is an amazing item2"})

    return item


@app.get("/cook")
async def cook(key: Annotated[str | None, Cookie()] = None):
    return {"key": key}


@app.get(
    "/response_items/{item_id}/name",
    response_model=Item,
    response_model_include={"name", "description"},
)
async def read_item_name(item_id: str):
    return items[item_id]


@app.get(
    "/response_items/{item_id}/public",
    response_model=Item,
    response_model_exclude={"tax"},
)
async def read_item_public_data(item_id: str):
    return items[item_id]


@app.get(
    "/response_items/{item_id}", response_model=Item, response_model_exclude_unset=False
)
async def read_response_item(item_id: str):
    res_item = items[item_id]
    print(res_item)
    return res_item


@app.get("/items/")
async def read_items(
    x: Annotated[
        list[str] | None,
        Query(
            alias="item-query",
            title="Query string list",
            description="desc",
            min_length=2,
        ),
    ],
    id: Annotated[str | None, AfterValidator(check_valid_id)] = None,
    # x: Annotated[str | None, Query(min_length=3)],
    q: Annotated[
        str | None,
        Query(min_length=3, max_length=50, pattern="^fix$"),
        # str | None, Query(min_length=3, max_length=50, pattern="^+*@.*\.com$" )
    ] = None,
    a: str | None = Query(deprecated=True, default=None, min_length=3, max_length=50),
    b: str | None = Query(
        include_in_schema=False,
        deprecated=True,
        default=None,
        min_length=3,
        max_length=50,
    ),
    skip: int = 0,
    limit: int = 5,
) -> list[Item]:
    # results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    results = {"items": fake_items_db[skip : skip + limit]}

    if x:
        results.update({"x": x})
    if q:
        results.update({"q": q})
    if a:
        results.update({"a": a})
    if b:
        results.update({"b": b})

    if id:
        item = data.get(id)
    else:
        id, item = random.choice(list(data.items()))
        results.update({"id": id, "name": item})

    return results


@app.get("/items/{item_id}")
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


@app.get("/models/{model_name}")
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


@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


@app.post("/user/")
async def create_user(user: UserIn) -> BaseUser:
    # パスワードを除いたパスワードを返すようにしたい
    # user_dict = user.model_dump()
    # user_dict.pop("password", None)
    # return BaseUser(**user_dict)
    return user


@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer


@app.post("/images/multiple/")
async def create_multiple_images(images: list[Image]):
    return images


# @app.post("/index-weights/")
# async def create_index_weights(weights: dict[int, float]):
#     return weights


@app.post("/items/", response_model=Item)
async def create_item(item: Item) -> Item:
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item


@app.put("/items/{item_id}")
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
    user: User,
    importance: Annotated[int, Body(gt=20)],
):
    # result = {"item_id": item_id, **item.model_dump()}
    result = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    # result = {"item_id": item_id, "item": item, "importance": importance}
    # result = {"item_id": item_id, "item": item}

    if q:
        result.update({"q": q})

    # if item:
    #     result.update({"item": item})

    return result
