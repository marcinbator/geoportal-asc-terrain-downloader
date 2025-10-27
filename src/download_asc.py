import math
import os
import re
import shutil

import requests
from pyproj import Transformer
from tqdm import tqdm


def download_asc(output_dir: str, geoportal_url: str, coords_wgs84: list[tuple[float, float]], clear_dirs=False):
    if clear_dirs:
        shutil.rmtree(output_dir)
        os.makedirs(output_dir)

    transformer = Transformer.from_crs("EPSG:4326", "EPSG:2180", always_xy=True)
    coords_2180 = [transformer.transform(lon, lat) for lat, lon in coords_wgs84]

    min_x = min(c[0] for c in coords_2180)
    max_x = max(c[0] for c in coords_2180)
    min_y = min(c[1] for c in coords_2180)
    max_y = max(c[1] for c in coords_2180)

    tile_size_meters = 2645

    os.makedirs(output_dir, exist_ok=True)

    url_template = geoportal_url
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
    with tqdm(total=(
            (math.ceil((max_x - min_x) / tile_size_meters)) * (math.ceil((max_y - min_y) / tile_size_meters)))) as pbar:
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

                    fix_header(filename)

                except Exception as e:
                    print(f"Downloading error: {bbox}: {e}")

                y += tile_size_meters
                pbar.update(1)
            x += tile_size_meters


def fix_header(filename):
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()

    has_dx = any(line.strip().startswith("dx") for line in lines)
    has_dy = any(line.strip().startswith("dy") for line in lines)
    has_cellsize = any("cellsize" in line.lower() for line in lines)
    has_nodata = any("nodata_value" in line.lower() for line in lines)

    new_lines = []

    if has_dx and has_dy:
        dx_value = "1.0000"

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("dx"):
                match = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                if match:
                    dx_value = match[0]
                continue
            elif stripped.startswith("dy"):
                continue
            new_lines.append(line)

        insert_idx = None
        for i, line in enumerate(new_lines):
            if line.strip().startswith("yllcorner"):
                insert_idx = i + 1
                break

        if insert_idx is None:
            insert_idx = len(new_lines)

        new_lines.insert(insert_idx, f"cellsize     {float(dx_value):.4f}\n")
        new_lines.insert(insert_idx + 1, "NODATA_value  0\n")

    elif has_cellsize:
        new_lines = list(lines)
        if not has_nodata:
            for i, line in enumerate(new_lines):
                if "cellsize" in line.lower():
                    new_lines.insert(i + 1, "NODATA_value  0\n")
                    break
    else:
        new_lines = lines

    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
