"""
Bulk post to stac-api
"""

import httpx
import json
import asyncio
from pathlib import Path
from constants import COLLECTION

api_url = 'https://drwgni8q1h.execute-api.us-west-2.amazonaws.com/'
collection = COLLECTION
url = f'{api_url}collections/{collection}/items'
print(url)

sem = asyncio.Semaphore(20)


async def post_item(client, file):
    async with sem:
        with open(file) as f:
            item = json.load(f)
            response = await client.post(url, json=item)
            print(file.name, response.status_code)


async def main():
    items = Path(COLLECTION)
    files = list(items.glob('*.json'))
    async with httpx.AsyncClient(timeout=60) as client:
        tasks = [post_item(client, file) for file in files]
        await asyncio.gather(*tasks)


asyncio.run(main())
