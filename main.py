from src.convert import convert_asc_to_tiff
from src.download_asc import download_asc

asc_directory = "out/tatry_asc_tiles"
download = False

if __name__ == "__main__":
    if download:
        download_asc(
            output_dir=asc_directory,
            coords_wgs84=[
                (49.29055, 19.70717),
                (49.30040, 20.23310),
                (49.13985, 20.23447),
                (49.14883, 19.72639)
            ]
        )

    convert_asc_to_tiff(
        asc_dir=asc_directory,
        output_dir="out/tiff",
        output_filename="tatry_heightmap_16bit.tiff"
    )
