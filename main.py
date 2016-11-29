#!/usr/bin/env python3

import aiofiles
import aiohttp
import asyncio
import json
import logging
import os
from aiohttp import web
from os import path


CALLBACK_URL = "http://127.0.0.1:5020/api/v1.0/downloaded"
NCBI_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


class DownloadJob:
    def __init__(self, accession, callback_id, email, filename, molecule_type):
        self.accession = accession
        self.callback_id = callback_id
        self.email = email
        self.filename = filename
        self.molecule_type = molecule_type

    @classmethod
    def from_dict(cls, data):
        accession = data.get("accession", None)
        callback_id = data.get("callback_id", None)
        email = data.get("email", None)
        filename = data.get("filename", None)
        molecule_type = data.get("molecule_type", None)
        if molecule_type not in ("protein", "nucleotide"):
            logging.debug("Ignoring invalid molecule_type %r, using 'nucleotide' instead", molecule_type)
            molecule_type = "nucleotide"
        return cls(accession, callback_id, email, filename, molecule_type)

    def to_dict(self):
        ret = {}
        if self.accession is not None:
            ret['accession'] = self.accession
        if self.callback_id is not None:
            ret['callback_id'] = self.callback_id
        if self.email is not None:
            ret['email'] = self.email
        if self.filename is not None:
            ret['filename'] = self.filename
        if self.molecule_type is not None:
            ret['molecule_type'] = self.molecule_type

        return ret

    def __str__(self):
        return "DownloadJob(accession:{j.accession}, callback_id:{j.callback_id}, email:{j.email}, filename:{j.filename}, molecule_type:{j.molecule_type})".format(j=self)


async def download_and_call(loop, job):
    async with aiohttp.ClientSession(loop=loop) as session:

        params = {
            'tool': 'antiSMASH downloader',
            'retmode': 'text',
            'id': job.accession,
        }

        if job.molecule_type == 'nucleotide':
            params['db'] = 'nucleotide'
            params['rettype'] = 'gbwithparts'
            file_ending = '.gbk'
        elif job.molecule_type == 'protein':
            params['db'] = 'protein'
            params['rettype'] = 'fasta'
            file_ending = '.fa'
        else:
            logging.warning("Invalid molecule_type %r, ignoring downlod.", job.molecule_type)
            return

        logging.error(job)
        outdir = job.callback_id
        os.makedirs(outdir, exist_ok=True)
        outfile = path.join(outdir, job.accession + file_ending)
        job.filename = outfile


        async with session.get(NCBI_URL, params=params) as response, aiofiles.open(outfile, 'wb') as fh:
            while True:
                # TODO: Check for known-bad content in the chunks here?
                chunk = await response.content.read(4096)
                if not chunk:
                    break
                await fh.write(chunk)

        await session.post(CALLBACK_URL, data=json.dumps(job.to_dict()).encode("utf-8"), headers={"Content-Type": "application/json; charset=utf-8"})


async def handleDownload(request):
    data = await request.json()
    job = DownloadJob.from_dict(data)
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(download_and_call(loop, job), loop=loop)
    return web.Response(status=202, text=json.dumps(job.to_dict()), content_type="application/json")


if __name__ == "__main__":
    app = web.Application()
    app.router.add_post("/api/v1.0/download", handleDownload)

    web.run_app(app, port=5021)
