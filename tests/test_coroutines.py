import aiohttp
import aiofiles
import json
import os
import pytest

from unittest import mock

from downloader import coroutines
from downloader.models import DownloadJob


@pytest.mark.asyncio
async def test_download_and_call_nucleotide(event_loop, monkeypatch, mocker, fake_client_session, fake_file, fake_response):
    fake_dl_job = DownloadJob('abcde', '123456', None, None, 'nucleotide')

    fake_session = fake_client_session._session
    fake_session.get = mocker.Mock(return_value=fake_response(b'This is not the sequence you are looking for'))
    fake_session.post = mocker.Mock(return_value=fake_response(b'', status=201))

    monkeypatch.setattr(aiohttp, 'ClientSession', fake_client_session)
    mocker.patch('aiofiles.open', return_value=fake_file)
    mocker.patch('os.makedirs')

    await coroutines.download_and_call(fake_dl_job, 'fake://entrez.url', 'fake://callback_url', event_loop)

    os.makedirs.assert_called_once_with('123456', exist_ok=True)
    aiofiles.open.assert_called_once_with('123456/abcde.gbk', 'wb')
    assert fake_file._buffer.getvalue() == b'This is not the sequence you are looking for'

    expected_params = {
        'tool': 'antiSMASH downloader',
        'retmode': 'text',
        'id': 'abcde',
        'db': 'nucleotide',
        'rettype': 'gbwithparts'
    }
    fake_session.get.assert_called_once_with('fake://entrez.url', params=expected_params)

    fake_session.post.assert_called_once_with('fake://callback_url',
        headers={"Content-Type": "application/json; charset=utf-8"},
        data=mocker.ANY)
    data = json.loads(fake_session.post.call_args[1]['data'].decode('utf-8'))
    expected = {
        'accession': 'abcde',
        'callback_id': '123456',
        'filename': '123456/abcde.gbk',
        'molecule_type': 'nucleotide',
    }
    assert expected == data


@pytest.mark.asyncio
async def test_download_and_call_protein(event_loop, monkeypatch, mocker, fake_client_session, fake_file, fake_response):
    fake_dl_job = DownloadJob('abcde', '123456', None, None, 'protein')

    fake_session = fake_client_session._session
    fake_session.get = mocker.Mock(return_value=fake_response(b'This is not the sequence you are looking for'))
    fake_session.post = mocker.Mock(return_value=fake_response(b'', status=201))

    monkeypatch.setattr(aiohttp, 'ClientSession', fake_client_session)
    mocker.patch('aiofiles.open', return_value=fake_file)
    mocker.patch('os.makedirs')

    await coroutines.download_and_call(fake_dl_job, 'fake://entrez.url', 'fake://callback_url', event_loop)

    os.makedirs.assert_called_once_with('123456', exist_ok=True)
    aiofiles.open.assert_called_once_with('123456/abcde.fa', 'wb')
    assert fake_file._buffer.getvalue() == b'This is not the sequence you are looking for'

    expected_params = {
        'tool': 'antiSMASH downloader',
        'retmode': 'text',
        'id': 'abcde',
        'db': 'protein',
        'rettype': 'fasta'
    }
    fake_session.get.assert_called_once_with('fake://entrez.url', params=expected_params)

    fake_session.post.assert_called_once_with('fake://callback_url',
        headers={"Content-Type": "application/json; charset=utf-8"},
        data=mocker.ANY)
    data = json.loads(fake_session.post.call_args[1]['data'].decode('utf-8'))
    expected = {
        'accession': 'abcde',
        'callback_id': '123456',
        'filename': '123456/abcde.fa',
        'molecule_type': 'protein',
    }
    assert expected == data
