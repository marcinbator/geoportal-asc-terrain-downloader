import os
import shutil

from src.convert import convert_asc_to_tiff
from src.download_asc import download_asc

asc_directory = "out/tatry_asc_tiles"
download = False

if __name__ == "__main__":
    top_left_bottom_right_coords = [
        (49.261330, 19.911765),
        (49.226664, 19.994461)
    ]

    if download:
        shutil.rmtree(asc_directory)
        os.makedirs(asc_directory)
        download_asc(
            output_dir=asc_directory,
            coords_wgs84=[
                top_left_bottom_right_coords[0],
                (top_left_bottom_right_coords[0][0], top_left_bottom_right_coords[1][1]),
                top_left_bottom_right_coords[1],
                (top_left_bottom_right_coords[1][0], top_left_bottom_right_coords[0][1])
            ]
        )

    convert_asc_to_tiff(
        asc_dir=asc_directory,
        output_dir="out/tiff",
        output_filename="tatry_heightmap_16bit.tiff"
    )
