'Coroutines dispatched by the REST API'
import aiofiles
import aiohttp
import json
import os
from aiohttp import log
from os import path


async def download_and_call(job, entrez_url, callback_url, loop):
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

        outdir = job.callback_id
        os.makedirs(outdir, exist_ok=True)
        outfile = path.join(outdir, job.accession + file_ending)
        job.filename = outfile


        async with session.get(entrez_url, params=params) as response, aiofiles.open(outfile, 'wb') as fh:
            while True:
                # TODO: Check for known-bad content in the chunks here?
                chunk = await response.content.read(4096)
                if not chunk:
                    break
                await fh.write(chunk)

        async with session.post(callback_url,
                data=json.dumps(job.to_dict()).encode("utf-8"),
                headers={"Content-Type": "application/json; charset=utf-8"}) as response:
            if response.status != 201:
                log.server_logger.error('callback returned %s', resp.status)
