# GEOPORTAL DTM converter

## Description
This tool allows to download any area available at [https://www.geoportal.gov.pl]()
as Digital Terrain Model map (bypassing its one-time download area limit) and save
it to `.asc` files, then convert them into one `.tiff` file containing grayscale
16 bit heightmap image.

This tool can be useful for creating high-resolution (1m of accuracy) real-world maps in simulators or 
games using tools such as Worldpainer for Minecraft.

## Instructions

### Prerequisites
- Python 3.11
- PIP

### Installation
1. Clone the repository
2. Install required dependencies using `pip install -r requirements.txt`

### Usage
1. Modify target geographical coordinates and save path as desired in `./main.py`
2. Run `./main.py` file