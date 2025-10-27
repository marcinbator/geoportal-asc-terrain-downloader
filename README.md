# GEOPORTAL .asc and .tiff downloader

## Description

This tool allows to download any area available at <https://www.geoportal.gov.pl>
as Digital Terrain Model map (bypassing its one-time download area limit) and save
it to `.asc` file, then convert them into one `.tiff` file containing grayscale
16 bit heightmap image.

This tool can be useful for creating high-resolution (1m of accuracy) real-world maps in simulators or to generate 3D 
terrain model using Blender and <https://github.com/marcinbator/asc-stl-blender-converter/blob/main/script.py> script.

## Instructions

### Prerequisites

- Python 3.11
- PIP

### Installation

1. Clone the repository
2. Install required dependencies using `pip install -r requirements.txt`

### Usage

1. Modify target geographical coordinates (top-left and bottom-right) and other settings as desired in `./main.py`
2. Run `./main.py` file