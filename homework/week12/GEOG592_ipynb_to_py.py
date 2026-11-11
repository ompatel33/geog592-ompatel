import sys
import argparse
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Ellipse
from matplotlib.backends.backend_pdf import PdfPages

### Refactor and generalize the cartography Jupyter Notebook you worked on last week, then convert it into a Python script that accepts two arguments. One argument is required and the other argument is not required, but it has a default value. Submit a link to your .py file.

parser = argparse.ArgumentParser(description="A program that makes a county land/water atlas")
parser.add_argument("statefp", help="The state's STATEFP code (e.g. 37 for NC, 20 for KS)")
parser.add_argument(
    "--color", default="#d8a1e1",
    help="Fill color for the highlighted county"
)
args = parser.parse_args()

statefp = args.statefp.zfill(2)  
county_color = args.color

# statefp = "20"

# Getting U.S. Census Data
print("Downloading data from US Census.")
url_0 = "https://www2.census.gov/geo/tiger/GENZ2024/shp/"
url_county = "cb_2024_us_county_500k.zip"  # county level
url_state = "cb_2024_us_state_500k.zip"    # state level

states = gpd.read_file(url_0 + url_state)
state_row = states.loc[states["STATEFP"] == statefp]
if state_row.empty:
    raise SystemExit(f"Error: '{statefp}' is not a valid STATEFP code.")
state_name = state_row["NAME"].iloc[0]
state_abbr = state_row["STUSPS"].iloc[0]

counties = gpd.read_file(url_0 + url_county)
state_counties = counties.loc[counties["STATEFP"] == statefp].copy()
# Since EPSG6543 only works for NC, let geopandas pick a UTM zone for selected state.
state_counties = state_counties.to_crs(state_counties.estimate_utm_crs())
state_counties = state_counties.sort_values("NAME").reset_index(drop=True)

## Code for county level data 
counties = gpd.read_file(url_0+url_county)
nc_counties = counties.loc[counties["STATEFP"] == "37"].to_crs(6543).copy()
# nc_counties.plot(edgecolor="black", facecolor="white")
nc_counties = nc_counties.sort_values("NAME").reset_index(drop=True)

# Plotting Functions
def county_map(county, ax, color):
    county.plot(ax=ax, edgecolor="black", facecolor=color)
    ax.set_axis_off()


def locator_map(county, all_counties, ax, color):
    all_counties.plot(ax=ax, edgecolor="gray", facecolor="white", linewidth=0.3)
    county.plot(ax=ax, edgecolor="black", facecolor=color)
    ax.set_axis_off()


def county_pie(county, ax):
    land = county["ALAND"].iloc[0]
    water = county["AWATER"].iloc[0]
    ax.pie(
        [land, water],
        labels=["Land", "Water"],
        colors=["olivedrab", "steelblue"],
        autopct="%.1f%%",
        startangle=90,
    )
    ax.set_title("Land and water")


def county_info(county, ax):
    land = county["ALAND"].iloc[0]
    water = county["AWATER"].iloc[0]

    ## Using AI and https://matplotlib.org/stable/gallery/shapes_and_collections/hatch_demo.html
    ax.add_patch(Polygon(
        [(0.02, 0.60), (0.09, 0.80), (0.14, 0.69), (0.19, 0.76), (0.25, 0.60)],
        facecolor="olivedrab", transform=ax.transAxes,
    ))
    ax.add_patch(Ellipse(
        (0.13, 0.30), width=0.23, height=0.12,
        facecolor="steelblue", transform=ax.transAxes,
    ))

    ax.text(0.32, 0.80,
            f"LAND\n{land / 1_000_000:,.2f} km²\n{land / 2_589_988.110336:,.2f} square miles",
            transform=ax.transAxes, fontsize=14, color="olivedrab", va="top")
    ax.text(0.32, 0.40,
            f"WATER\n{water / 1_000_000:,.2f} km²\n{water / 2_589_988.110336:,.2f} square miles",
            transform=ax.transAxes, fontsize=14, color="steelblue", va="top")
    ax.set_axis_off()


def county_figure(county, all_counties, state_name, color, pdf):
    fig = plt.figure(figsize=(12, 8))
    # [left, bottom, width, height] as fractions of the figure (coded with AI help)
    ax_county = fig.add_axes([0.05, 0.23, 0.55, 0.54])
    ax_locator = fig.add_axes([0.05, 0.08, 0.25, 0.12])
    ax_pie = fig.add_axes([0.65, 0.48, 0.30, 0.30])
    ax_info = fig.add_axes([0.65, 0.12, 0.30, 0.32])

    county_map(county, ax_county, color)
    locator_map(county, all_counties, ax_locator, color)
    county_pie(county, ax_pie)
    county_info(county, ax_info)

    fig.text(0.05, 0.94, f"{state_name.upper()} / County Water-Land Atlas",
             fontsize=10, color="olivedrab")
    # NAMELSAD handles "Durham County", "Orleans Parish", etc.
    fig.text(0.05, 0.87, county["NAMELSAD"].iloc[0], fontsize=28, fontweight="bold")
    fig.text(0.05, 0.03, "Source: U.S. Census Bureau | Areas from ALAND and AWATER",
             fontsize=9, color="gray")

    pdf.savefig(fig)
    plt.close(fig)

# Atlas Construction
output_file = f"{state_abbr}_Counties.pdf"
print(f"Building atlas for {state_name} ({len(state_counties)} counties)...")

### takes a few seconds
with PdfPages(output_file) as pdf:  # `with` cleans up the PDF automatically when done
    for i in range(len(state_counties)):
        county_figure(state_counties.iloc[[i]], state_counties, state_name, county_color, pdf)

print(f"Saved {output_file}")

# Code polished with AI assistance.
## Helped with syntax, debugging errors, and code organization primarily.
### Had issues with importing from the Jupyter Notebook, so I copied the functions into this script instead.