"""
Bulk post to stac-api
"""

import json
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

api_url = "https://drwgni8q1h.execute-api.us-west-2.amazonaws.com/"
collection = "dem-phase3"

url = f"{api_url}collections/{collection}/items"
num_workers = 28

file_path = Path(collection)
files = list(file_path.glob("*.json"))


def post_item(file):
    try:
        with open(file, "r") as f:
            payload = json.load(f)

        response = requests.post(url, json=payload)

        print(f"{file.name}: {response.status_code}")

        return response.status_code, file.name

    except Exception as e:
        print(f"{file.name}: ERROR {e}")
        return None


def main():
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(post_item, file) for file in files]

        for future in as_completed(futures):
            future.result()


if __name__ == "__main__":
    main()