import os
import re

import imageio.v3 as iio
import numpy as np


def convert_asc_to_tiff(asc_dir: str, output_filename: str, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    merged_data, header = merge_asc_tiles(asc_dir)

    asc_path = os.path.join(output_dir, output_filename +".asc")
    save_asc(asc_path, merged_data, header)
    print(f"Saved merged ASC: {asc_path}")

    tiff_path = os.path.join(output_dir, output_filename + ".tiff")
    save_tiff(tiff_path, merged_data)
    print(f"Saved TIFF: {tiff_path}")


#


def read_asc_header(path):
    header = {}
    with open(path, "r") as f:
        for _ in range(6):
            line = f.readline()
            parts = line.strip().split()
            if len(parts) >= 2:
                header[parts[0].lower()] = float(parts[1])
    return header


def read_asc_data(path):
    header = read_asc_header(path)
    with open(path, "r") as f:
        for _ in range(6):
            f.readline()
        data = np.loadtxt(f)
    return header, data


def find_tiles(asc_dir):
    tiles = []
    for f in os.listdir(asc_dir):
        if f.endswith(".asc"):
            match = re.search(r"dtm_(\d+)_(\d+)\.asc", f)
            if match:
                x, y = map(int, match.groups())
                tiles.append((x, y, os.path.join(asc_dir, f)))
    return tiles


def merge_asc_tiles(asc_dir):
    tiles = find_tiles(asc_dir)
    positions = []

    for _, _, path in tiles:
        header, _ = read_asc_data(path)
        xllcorner = header["xllcorner"]
        yllcorner = header["yllcorner"]
        ncols = int(header["ncols"])
        nrows = int(header["nrows"])
        cellsize = header.get("cellsize", 1.0)
        positions.append((xllcorner, yllcorner, ncols, nrows, cellsize, path))

    cell_sizes = [p[4] for p in positions]
    res = float(np.mean(cell_sizes))

    min_x = min(p[0] for p in positions)
    min_y = min(p[1] for p in positions)
    max_x = max(p[0] + p[2] * p[4] for p in positions)
    max_y = max(p[1] + p[3] * p[4] for p in positions)

    map_width = int((max_x - min_x) / res)
    map_height = int((max_y - min_y) / res)
    print(f"Map shape: {map_width} x {map_height}")

    full_map = np.full((map_height, map_width), np.nan, dtype=np.float32)

    for xllcorner, yllcorner, ncols, nrows, cellsize, path in positions:
        _, data = read_asc_data(path)
        x_snap = round((xllcorner - min_x) / cellsize) * cellsize + min_x
        y_snap = round((yllcorner - min_y) / cellsize) * cellsize + min_y

        x_start = int(round((x_snap - min_x) / cellsize))
        y_start = int(round((max_y - y_snap) / cellsize)) - nrows

        print(f"{path}: x_start={x_start}, y_start={y_start}, shape={data.shape}")

        tile_h, tile_w = data.shape
        y_end = y_start + tile_h
        x_end = x_start + tile_w

        if y_end > full_map.shape[0]:
            overlap_h = y_end - full_map.shape[0]
            tile_h -= overlap_h
            y_end = y_start + tile_h

        if x_end > full_map.shape[1]:
            overlap_w = x_end - full_map.shape[1]
            tile_w -= overlap_w
            x_end = x_start + tile_w

        full_map[y_start:y_end, x_start:x_end] = data[:tile_h, :tile_w]

    if np.any(np.isnan(full_map)):
        from scipy.signal import convolve2d

        kernel = np.ones((5, 5))
        sum_vals = convolve2d(np.nan_to_num(full_map), kernel, mode='same', boundary='symm')
        count_vals = convolve2d(~np.isnan(full_map), kernel, mode='same', boundary='symm')
        full_map = np.where(np.isnan(full_map), sum_vals / np.maximum(count_vals, 1), full_map)

    merged_header = {
        "ncols": map_width,
        "nrows": map_height,
        "xllcorner": min_x,
        "yllcorner": min_y,
        "cellsize": res,
        "nodata_value": -9999
    }

    return full_map, merged_header


def save_asc(path, data, header):
    with open(path, "w") as f:
        f.write(f"ncols         {header['ncols']}\n")
        f.write(f"nrows         {header['nrows']}\n")
        f.write(f"xllcorner     {header['xllcorner']}\n")
        f.write(f"yllcorner     {header['yllcorner']}\n")
        f.write(f"cellsize      {header['cellsize']}\n")
        f.write(f"NODATA_value  {header['nodata_value']}\n")
        np.savetxt(f, data, fmt="%.2f")


def save_tiff(path, data):
    min_val = np.min(data)
    max_val = np.max(data)
    normalized = ((data - min_val) / (max_val - min_val) * 65535).astype(np.uint16)
    iio.imwrite(path, normalized, extension=".tiff")
