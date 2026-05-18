"""
This script will rename the assets "asset" to "data" for uniformity across ortho and dem collections.
"""

import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
# from constants import COLLECTION

collection = 'laz-phase3' 
p = Path(f'C:/Users/Ian.Horn/Documents/stac-repos/items/{collection}')

glob_list = list(p.glob('*.json'))


def rename_asset(file):

    with open(file, encoding="utf-8") as f:
        data = json.load(f)

    # clear links
    data["links"] = []
    
    file_base = file.stem[:8]
    
    assets= data.get('assets', {})

    # Rename "pointcloud" asset key to "data"
    if "pointcloud" in assets:
        assets["data"] = assets.pop("pointcloud")
        # Update MIME type
        if assets["data"].get("type") == "application/octet-stream":
            assets["data"]["type"] = "application/vnd.laszip+copc"

    if 'thumbnail' in assets:
        None
    else:
        data['assets']['thumbnail'] = {
            "href": f'https://kyfromabove-stac/items/thumbnails/{collection}/{file_base}_Intensity_Phase3.png',
            "type": "image/png",
            "roles": ["thumbnail"],
            "title": 'Thumbnail'
        }

# Reorder assets so "data" comes first, then "thumbnail"

    assets = data.get("assets", {})

    new_assets = {}

    if "data" in assets:
        new_assets["data"] = assets["data"]

    if "thumbnail" in assets:
        new_assets["thumbnail"] = assets["thumbnail"]

    # Keep any remaining assets afterward
    for key, value in assets.items():
        if key not in new_assets:
            new_assets[key] = value

    data["assets"] = new_assets
        
    with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    return file

def main():

    # Run in parallel on folder
    with ThreadPoolExecutor(max_workers=10) as executor:
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