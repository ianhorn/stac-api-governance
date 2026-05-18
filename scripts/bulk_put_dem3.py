import json
import asyncio
from pathlib import Path
import aiohttp
import async_timeout

FOLDER = Path(r'C:\Users\Ian.Horn\Documents\stac-repos\items\dem-phase2')
PHASE = "dem-phase2"
API_URL_BASE = 'https://drwgni8q1h.execute-api.us-west-2.amazonaws.com/collections/'

# Concurrency control
SEM = asyncio.Semaphore(28)
MAX_RETRIES = 1
TIMEOUT = 30  # seconds


async def put_item(session, file_path):
    """PUT (update) a single STAC item, retrying on failure."""
    async with SEM:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                # Load JSON
                with open(file_path, "r", encoding="utf-8") as f:
                    item = json.load(f)

                item_id = item["id"]
                put_url = f"{API_URL_BASE}{PHASE}/items/{item_id}"

                # Send PUT request
                async with async_timeout.timeout(TIMEOUT):
                    async with session.put(
                        put_url,
                        json=item,
                        headers={"Content-Type": "application/json"},
                    ) as response:

                        if response.status in (200, 201):
                            print(f"✅ Updated {file_path.name}")
                            return True
                        elif response.status == 404:
                            print(f"❌ Not found (404) {file_path.name} → cannot PUT new items")
                            return False
                        else:
                            text = await response.text()
                            print(f"❌ Attempt {attempt}: {file_path.name} → {response.status}")
                            print(text)

            except Exception as e:
                print(f"💥 Attempt {attempt} error with {file_path.name}: {e}")

            # Backoff between retries
            await asyncio.sleep(2 * attempt)

        print(f"❌ Failed after {MAX_RETRIES} attempts: {file_path.name}")
        return False


async def main():
    # Find all JSON files recursively
    files = list(FOLDER.rglob("*.json"))
    print(f"Bulk PUT {len(files)} files to {PHASE}")

    if not files:
        print(f"⚠️ No JSON files found in {FOLDER}")
        return

    async with aiohttp.ClientSession() as session:
        tasks = [put_item(session, f) for f in files]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())