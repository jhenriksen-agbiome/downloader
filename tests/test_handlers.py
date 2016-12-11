from aiohttp import web

from downloader import handlers
from downloader import version
from downloader.app import generate_app

async def test_download(test_client, loop, mocker, monkeypatch):

    async def fake_coroutine(job, entrez_url, callback_url, loop):
        pass

    monkeypatch.setattr(handlers, 'download_and_call', fake_coroutine)

    mocker.spy(handlers, 'download_and_call')

    app = generate_app(loop=loop)
    client = await test_client(app)
    resp = await client.post('/api/v1.0/download', data=b'{"accession": "abcd", "callback_id": "12345"}')
    assert 202 == resp.status

    handlers.download_and_call.assert_called_once_with(
        mocker.ANY,
        'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi',
        'http://127.0.0.1:5020/api/v1.0/downloaded',
        loop=mocker.ANY
    )


async def test_version(test_client, loop):
    app = generate_app(loop=loop)
    client = await test_client(app)
    resp = await client.get('/api/v1.0/version')
    assert 200 == resp.status
    data = await resp.json()

    assert {'api_version': version.__version__} == data
