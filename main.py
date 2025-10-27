from src.convert import convert_asc_to_tiff
from src.download_asc import download_asc

asc_directory = "out/asc_tiles"
output_filename = "heightmap"
download = True
clean_dir = False
GEOPORTAL_URL = 'https://mapy.geoportal.gov.pl/wss/service/PZGIK/NMT/GRID1/WCS/DigitalTerrainModel'

top_left_bottom_right_coords = [
    (49.261330, 19.911765),
    (49.226664, 19.994461)
]

if __name__ == "__main__":
    if download:
        download_asc(
            output_dir=asc_directory,
            geoportal_url=GEOPORTAL_URL,
            coords_wgs84=[
                top_left_bottom_right_coords[0],
                (top_left_bottom_right_coords[0][0], top_left_bottom_right_coords[1][1]),
                top_left_bottom_right_coords[1],
                (top_left_bottom_right_coords[1][0], top_left_bottom_right_coords[0][1])
            ],
            clear_dirs=clean_dir
        )

    convert_asc_to_tiff(
        asc_dir=asc_directory,
        output_dir="out",
        output_filename=output_filename
    )
