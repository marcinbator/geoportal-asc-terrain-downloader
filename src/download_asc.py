import os
import math
import requests
from pyproj import Transformer
from tqdm import tqdm

from src.var import GEOPORTAL_URL


def download_asc(output_dir: str, coords_wgs84: list[tuple[float, float]]):
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:2180", always_xy=True)
    coords_2180 = [transformer.transform(lon, lat) for lat, lon in coords_wgs84]
    
    min_x = min(c[0] for c in coords_2180)
    max_x = max(c[0] for c in coords_2180)
    min_y = min(c[1] for c in coords_2180)
    max_y = max(c[1] for c in coords_2180)
    
    tile_size_meters = 2645
    
    os.makedirs(output_dir, exist_ok=True)
    
    url_template = GEOPORTAL_URL
    params_template = {
        "service": "wcs",
        "request": "GetCoverage",
        "version": "1.0.0",
        "coverage": "DTM_PL-KRON86-NH",
        "format": "image/x-aaigrid",
        "resx": "1",
        "resy": "1",
        "crs": "EPSG:2180"
    }
    
    x = min_x
    with tqdm(total=((math.ceil((max_x - min_x) / tile_size_meters)) * (math.ceil((max_y - min_y) / tile_size_meters)))) as pbar:
        while x < max_x:
            y = min_y
            while y < max_y:
                x1 = x
                y1 = y
                x2 = min(x + tile_size_meters, max_x)
                y2 = min(y + tile_size_meters, max_y)
    
                bbox = f"{x1},{y1},{x2},{y2}"
                params = params_template.copy()
                params["bbox"] = bbox
    
                filename = os.path.join(output_dir, f"dtm_{int(x1)}_{int(y1)}.asc")
    
                try:
                    response = requests.get(url_template, params=params, timeout=60)
                    response.raise_for_status()
                    with open(filename, "wb") as f:
                        f.write(response.content)
                except Exception as e:
                    print(f"Downloading error: {bbox}: {e}")
    
                y += tile_size_meters
                pbar.update(1)
            x += tile_size_meters

