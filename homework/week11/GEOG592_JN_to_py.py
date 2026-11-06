import sys
import argparse
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from GEOG592_JN_to_py import locator_map, county_figure, county_map, county_info, county_pie, PdfPages

parser = argparse.ArgumentParser(
    description="A program that makes an Atlas"
)
parser.add_argument("statefp", help="The STATEFP code")
parser.add_argument(
    "--color", default="#d8a1e1",
    help="Number of greetings (default: 1)"
)
args = parser.parse_args()
statefp=args.statefp

# statefp = "20"

# Getting U.S. Census Data
print("Downloading data from CENSUS")
url_0 = "https://www2.census.gov/geo/tiger/GENZ2024/shp/"
url_county = "cb_2024_us_county_500k.zip" # county level
url_state = "cb_2024_us_state_500k.zip" # state level 

## Code for county level data 

counties = gpd.read_file(url_0+url_county)
nc_counties = counties.loc[counties["STATEFP"] == "37"].to_crs(6543).copy()
# nc_counties.plot(edgecolor="black", facecolor="white")
nc_counties = nc_counties.sort_values("NAME").reset_index(drop=True)

locator_map()
county_pie("Orange")
county_figure("Orange")
county_info("Orange")

# This might take a few seconds and you need at least 40MB of free space in your computer
with PdfPages("NC_Counties.pdf") as pdf:  #with #manages a resource and automatically cleans up when you finish using it.
    for county in nc_counties["NAME"]:
        county_figure(county, pdf)