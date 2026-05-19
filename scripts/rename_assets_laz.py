"""
This script will rename the assets "asset" to "data" for uniformity across ortho and dem collections.
"""

import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from constants import COLLECTION

collection = 'laz-phase3' 
p = Path(f'C:/Users/Ian.Horn/Documents/stac-repos/items/{collection}')

glob_list = list(p.glob('*.json'))


def rename_asset(file):

    with open(file, encoding="utf-8") as f:
        data = json.load(f)

    data["stac_version"] = "1.1.0"

    # clear links
    data["links"] = []

    assets = data.get("assets", {})
    new_assets = {}

    # --- DATA ---
    if "pointcloud" in assets:
        new_assets["data"] = {
            **assets["pointcloud"],
            "type": "application/vnd.laszip+copc",
            "title": "copc data",
            "roles": ["data"]
        }

    elif "data" in assets:
        new_assets["data"] = {
            **assets["data"],
            "type": "application/vnd.laszip+copc",
            "title": "copc data",
            "roles": ["data"]
        }
    else:
        raise KeyError(f"No pointcloud/data asset found in {file}")
    
    # remove legacy/duplicate assets
    assets.pop("pointcloud", None)
    assets.pop("asset", None)

    # thumbnail second
    if "thumbnail" in assets:
        old_href = assets["thumbnail"]["href"]
        filename = Path(old_href).name

    else:
        # derive thumbnail filename from data asset
        data_href = new_assets["data"]["href"]
        filename = Path(data_href).with_suffix(".png").name

    new_assets["thumbnail"] = {
        "href": (
            f"https://kyfromabove-stac.s3.us-west-2.amazonaws.com/"
            f"collections/{collection}/thumbnails/{filename}"
        ),
        "type": "image/png",
        "roles": ["thumbnail"],
        "title": "thumbnail"
    }

    data_href = new_assets["data"]["href"]

    # preserve any additional assets after the main three
    for k, v in assets.items():
        if k not in {
            "asset",
            "data",
            "metadata",
            "worldfile",
            "thumbnail",
        }:
            new_assets[k] = v

    data["assets"] = new_assets

    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return file

def main():

    # Run in parallel on folder
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_file = {
            executor.submit(rename_asset, file): file
            for file in glob_list
        }

        for future in as_completed(future_file):
            file = future_file[future]
            try:
                result = future.result()
                print(f"Updated: {result}")
            except Exception as exc:
                print(f"{file} generated an exception: {exc}")

    
if __name__ == '__main__':
    main()