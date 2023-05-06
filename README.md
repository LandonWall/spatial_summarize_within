# Spatial Summarize Within

Spatial Summarize Within is a Python package that simplifies the process of summarizing attribute data within overlapping geometries in shapefiles. Given two shapefiles, it calculates the weighted sums of specified attributes based on the overlap percentages between the input shapefile and the overlay shapefile.

## Installation

You can install Spatial Summarize Within using pip:

```bash
pip install spatial_summarize_within
```
Geo Summarizer has the following dependencies, which will be installed automatically:

geopandas
pandas
shapely
mapclassifier

# Usage
To use Spatial Summarize Within you'll first need to import the summarize_within function:
from spatial_summarize_within.summarize_within import summarize_within

Next, call the summarize_within function with your input and overlay shapefiles, the columns you want to sum, and the key to group the results by:
```
input_shapefile = gpd.read_file("path/to/your/input_shapefile.shp")
overlay_shapefile = gpd.read_file("path/to/your/overlay_shapefile.shp")

result = summarize_within(
    input_shapefile=input_shapefile,
    overlay_shapefile=overlay_shapefile,
    columns_to_sum=[
        # List the columns you want to sum, e.g.:
        "column1",
        "column2",
        "column3",
    ],
    key_to_group_by="your_group_by_key"
)
```
The result variable will contain a GeoDataFrame with the summarized data.

# Example
In this example, we will summarize population data within an input shapefile using an overlay shapefile.

```
from spatial_summarize_within.summarize_within import summarize_within
import geopandas as gpd

# Load input and overlay shapefiles
input_shapefile = gpd.read_file("path/to/your/input_shapefile.shp")
overlay_shapefile = gpd.read_file("path/to/your/overlay_shapefile.shp")

# Call the summarize_within function
result = summarize_within(
    input_shapefile=input_shapefile,
    overlay_shapefile=overlay_shapefile,
    columns_to_sum=[
        "total_population",
        "urban_population",
        "rural_population",
    ],
    key_to_group_by="region_id"
)

# Save the result to a new shapefile
result.to_file("path/to/your/output_shapefile.shp")
```
