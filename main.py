import uvicorn
import os
from random import randint, seed
from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from jinja2 import Template
from words import WORDS_LEN, words_db

FIELD_SIZE = 20
ROOT_PATH = os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir))

app = FastAPI()
app.mount("/static", StaticFiles(directory=os.path.join(ROOT_PATH, 'static')), name="static")

NONE = 'none-button'
RED = 'red-button'
BLUE = 'blue-button'
BLACK = 'black-button'

words = []
colors = []
opened = [False] * FIELD_SIZE


def load_file(filename: str):
    with open(os.path.join(ROOT_PATH, filename), "r") as file:
        return file.read()


@app.get('/')
async def index():
    html_template = load_file("index.html")
    return Response(content=html_template, media_type="text/html")


def draw_game(capitan: bool):

    global colors, words, opened

    html_template = load_file("game.html")
    html_buttons = ""

    i = 0
    for _ in range(4):
        for _ in range(5):
            if capitan or opened[i]:
                html_button = "<button id=\"{{id}}\" class=\"{{color}}\" type=\"button\">{{word}}</button>\n"
            else:
                html_button = "<button id=\"{{id}}\" class=\"\" type=\"button\" onclick=\"goto('/open/{{i}}')\">{{word}}</button>\n"

            h = Template(html_button).render(id=f'word{i}', color=colors[i], word=words[i], i=i)
            html_buttons += h
            i += 1
        html_buttons += "</br>"

    html_template = html_template.replace('%buttons%', html_buttons)

    red_score = len([r for r in colors if r == RED]) - len([r for r in opened if r == RED])
    blue_score = len([r for r in colors if r == BLUE]) - len([r for r in opened if r == BLUE])
    html = Template(html_template).render(red_score=red_score, blue_score=blue_score)
    return html


def init_game():
    global words, colors, opened

    words = [words_db[randint(0, WORDS_LEN - 1)] for _ in range(FIELD_SIZE)]
    colors = [NONE] * FIELD_SIZE
    opened = [False] * FIELD_SIZE

    def fill_color(words_number, color):
        w = words_number
        while w > 0:
            i = randint(0, FIELD_SIZE - 1)
            if colors[i] == NONE:
                colors[i] = color
                w -= 1

    fill_color(4, BLUE)
    fill_color(5, RED)
    fill_color(1, BLACK)


@app.get('/new_game')
async def new_game():
    init_game()
    html_template = load_file("index.html")
    return Response(content=html_template, media_type="text/html")


@app.get('/game')
async def game():
    global words
    if not words:
        init_game()
    html = draw_game(False)
    return Response(content=html, media_type="text/html")


@app.get('/capitan')
async def game():
    global words
    if not words:
        init_game()
    html = draw_game(True)
    return Response(content=html, media_type="text/html")


@app.get('/open/{word_id}')
async def open_word(word_id: int):
    global colors, opened
    opened[word_id] = colors[word_id]
    html = draw_game(False)
    return Response(content=html, media_type="text/html")


if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=11000, reload=True)
