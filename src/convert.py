import os
import numpy as np
import imageio.v3 as iio
import re

def convert_asc_to_tiff(asc_dir: str, output_filename: str, output_dir="out/tiff"):
    res=1
    tiles = []
    for f in os.listdir(asc_dir):
        if f.endswith(".asc"):
            match = re.search(r"dtm_(\d+)_(\d+)\.asc", f)
            if match:
                x, y = map(int, match.groups())
                tiles.append((x, y, os.path.join(asc_dir, f)))
    
    positions = []
    
    for x, y, path in tiles:
        with open(path, "r") as f:
            header = {}
            for _ in range(6):
                line = f.readline()
                parts = line.strip().split()
                if len(parts) >= 2:
                    key = parts[0].lower()
                    val = parts[1]
                    header[key] = float(val)
    
            xllcorner = header["xllcorner"]
            yllcorner = header["yllcorner"]
            ncols = int(header["ncols"])
            nrows = int(header["nrows"])
            if "cellsize" in header:
                cellsize = header["cellsize"]
            elif "dx" in header and "dy" in header and header["dx"] == header["dy"]:
                cellsize = header["dx"]
            else:
                cellsize = 1.0
    
            positions.append((xllcorner, yllcorner, ncols, nrows, path))
    
    min_x = min(p[0] for p in positions)
    min_y = min(p[1] for p in positions)
    max_x = max(p[0] + p[2] * res for p in positions)
    max_y = max(p[1] + p[3] * res for p in positions)
    
    map_width = int((max_x - min_x) / res)
    map_height = int((max_y - min_y) / res)
    
    print(f"Map shape: {map_width} x {map_height}")
    
    full_map = np.full((map_height, map_width), np.nan, dtype=np.float32)
    
    for xllcorner, yllcorner, ncols, nrows, path in positions:
        with open(path, "r") as f:
            for _ in range(6):
                f.readline()
            data = np.loadtxt(f)
    
        x_start = round((xllcorner - min_x) / cellsize)
        y_start = round((max_y - yllcorner) / cellsize) - nrows
    
        print(f"{path}: x_start={x_start}, y_start={y_start}, shape={data.shape}")
    
        tile_h, tile_w = data.shape
        target = full_map[y_start:y_start + tile_h, x_start:x_start + tile_w]
    
        h_target, w_target = target.shape
        h_data, w_data = data.shape
    
        min_h = min(h_target, h_data)
        min_w = min(w_target, w_data)
    
        target[:min_h, :min_w] = data[:min_h, :min_w]
    
    nan_mask = np.isnan(full_map)
    full_map[nan_mask] = np.nanmin(full_map)
    
    min_val = np.min(full_map)
    max_val = np.max(full_map)
    normalized = ((full_map - min_val) / (max_val - min_val) * 65535).astype(np.uint16)

    os.makedirs(output_dir, exist_ok=True)
    iio.imwrite(os.path.join(output_dir, output_filename), normalized.astype(np.uint16), extension=".tiff")
    print(f"Saved {output_dir}/{output_filename} as 16-bit TIFF")

