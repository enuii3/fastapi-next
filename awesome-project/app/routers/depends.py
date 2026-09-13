from typing import Annotated
from fastapi import Depends, APIRouter, Cookie

router = APIRouter()


class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}


CommonsDep = Annotated[CommonQueryParams, Depends()]

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@router.get("/common-users/")
async def read_common_users(commons: CommonsDep):
    return commons


@router.get("/common-items/")
async def read_common_items(commons: CommonsDep):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip : commons.skip + commons.limit]
    response.update({"items": items})
    return response


def query_extractor(q: str | None = None):
    if q == "test":
        q = "japan"
    return q


def query_or_cookie_extractor(
    q: Annotated[str, Depends(query_extractor)],
    last_query: Annotated[str | None, Cookie()] = "hogehoge",
):
    if not q:
        return {"last_query": last_query}
    return {"q": q}


@router.get("/items/")
async def read_query(
    query_or_default: Annotated[dict, Depends(query_or_cookie_extractor)],
):
    # return {"q_or_cookie": query_or_default}
    return query_or_default


from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException

data = {
    "plumbus": {"description": "Freshly pickled plumbus", "owner": "Morty"},
    "portal-gun": {"description": "Gun to create portals", "owner": "Rick"},
}


class OwnerError(Exception):
    pass


def get_username():
    try:
        yield "Rick"
    except OwnerError as e:
        print("e is", e)
        print("e.args is", e.args)
        raise HTTPException(status_code=400, detail=f"Owner error: {e}")


@router.get("/owner_items/{item_id}")
def get_owner_item(item_id: str, username: Annotated[str, Depends(get_username)]):
    if item_id not in data:
        raise HTTPException(status_code=404, detail="Item not found")
    item = data[item_id]
    if item["owner"] != username:
        raise OwnerError([username, "hoge"])
    return item
