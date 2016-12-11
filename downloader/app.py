#!/usr/bin/env python3

from aiohttp import web
from envparse import Env

from .handlers import generate_routes


def generate_app(loop=None):

    env = Env(
        ASDL_ENTREZ_URL=dict(default="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"),
        ASDL_CALLBACK_URL=dict(default="http://127.0.0.1:5020/api/v1.0/downloaded")
    )

    app = web.Application(loop=loop)
    app['config'] = env

    generate_routes(app)
    return app
