import json
from pathlib import Path

import httpx

output_dir = Path('dem-phase1')

BASE_URL = f'https://spved5ihrl.execute-api.us-west-2.amazonaws.com/collections/{output_dir}/items'


output_dir.mkdir(exist_ok=True)

url = BASE_URL
count = 0

with httpx.Client(timeout=60) as client:

    while url:
        print(f"Fetching: {url}")

        response = client.get(url)
        response.raise_for_status()

        data = response.json()

        features = data.get("features", [])

        for item in features:
            item_id = item["id"]

            out_file = output_dir / f"{item_id}.json"

            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(item, f, indent=2)

            count += 1
            print(f"Saved: {out_file.name}")

        # Find next page
        next_link = None

        for link in data.get("links", []):
            if link.get("rel") == "next":
                next_link = link.get("href")
                break

        url = next_link

print(f"\nDownloaded {count} items.")