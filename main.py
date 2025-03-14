import random
import string

from fastapi import FastAPI, Form, status
from fastapi.responses import FileResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="public")

letters = string.ascii_letters
numbers = "0123456789"
chars = letters + numbers

storage = dict()

# todo: change -> zip.py/
domain = "http://localhost:8000/"


@app.get("/")
async def root():
    return FileResponse("public/index.html")


# is short link free
def is_available(short_link):
    for item in storage:
        if item == short_link:
            return False

    return True


# is long link duplicate
def is_duplicate(long_link):
    for item in storage:
        if storage[item] == long_link:
            return item

    return False


def generate_link(user_link):
    result = ""

    for _ in range(5):
        result += random.choice(chars)

    storage[result] = user_link

    return domain + result


def shortener(user_link):
    if not is_duplicate(user_link):
        short_link = generate_link(user_link)

        if is_available(short_link):
            return short_link
        else:
            short_link = generate_link(user_link)

    else:
        short_link = domain + is_duplicate(user_link)

    return short_link


# todo: cut link in this method
@app.post("/result")
async def encode_link(request: Request, userlink: str = Form()):
    result = shortener(userlink)

    return templates.TemplateResponse(
        "result.html", {"request": request, "result": result}
    )


@app.get("/show_links")
async def show_links():
    return {"All links": storage}


@app.get("/{short_link}")
async def decode_link(short_link):
    if short_link == "favicon.ico":
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    try:
        return RedirectResponse(storage[short_link])
    except KeyError:
        print(f"Error! Link: [{short_link}] not in storage")
