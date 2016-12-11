'Handlers for antiSMASH downloader'
import asyncio
import json
from aiohttp import web
from aiohttp_route_decorator import RouteCollector, Route

from .coroutines import download_and_call
from .models import DownloadJob
from .version import __version__

async def download(request):
    'Trigger a download from ENTREZ'

    data = await request.json()
    job = DownloadJob.from_dict(data)

    entrez_url = request.app['config']('ASDL_ENTREZ_URL')
    callback_url = request.app['config']('ASDL_CALLBACK_URL')

    loop = request.app.loop
    asyncio.ensure_future(download_and_call(job, entrez_url, callback_url, loop=loop), loop=loop)
    return json_response(job.to_dict(), status=202)


async def version(request):
    ret = {
        'api_version': __version__,
    }
    return json_response(ret)


######### Route setup ##########

def generate_routes(app):
    routes = RouteCollector(prefix="/api/v1.0", routes=[
        Route('/version', version, method='GET'),
        Route('/download', download, method='POST'),
    ])

    routes.add_to_router(app.router)


######### Helper functions ##############

def json_response(data, **kwargs):
    '''Return a JSON response'''
    kwargs.setdefault('content_type', 'application/json')
    return web.Response(text=json.dumps(data), **kwargs)
