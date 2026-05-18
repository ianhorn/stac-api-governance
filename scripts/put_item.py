"""
Bulk put to stac-api
"""

import httpx
import json
import asyncio
from pathlib import Path
from constants import COLLECTION

api_url = 'https://drwgni8q1h.execute-api.us-west-2.amazonaws.com'
collection_id = COLLECTION

sem = asyncio.Semaphore(20)


async def put_item(client, file):

    async with sem:

        with open(file, encoding='utf-8') as f:
            item = json.load(f)

        item_id = item["id"]

        url = f'{api_url}/collections/{collection_id}/items/{item_id}'

        response = await client.put(url, json=item)

        print(item_id, response.status_code)

    return item_id


async def main():

    items = Path(COLLECTION)

    files = list(items.glob('*.json'))

    async with httpx.AsyncClient(
        timeout=60,
        follow_redirects=True
    ) as client:

        tasks = [put_item(client, file) for file in files]

        await asyncio.gather(*tasks)


asyncio.run(main())