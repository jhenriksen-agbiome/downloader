from aiohttp import web
from downloader.app import generate_app

app = generate_app()

if __name__ == "__main__":
    web.run_app(app, port=5021)
