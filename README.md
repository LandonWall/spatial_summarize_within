# Spatial Summarize Within
Spatial Summarize Within is a Python package that simplifies the process of summarizing attribute data within overlapping geometries in shapefiles. Given two shapefiles, it calculates the weighted values of specified attributes based on the overlap percentages between the input shapefile and the overlay shapefile. The statistics are calculated using only the proportion of the area that is within the boundary.
## Usage
Full [Tutorial](https://github.com/LandonWall/summarize_within_example/blob/master/notebooks/Summarize%20Precinct%20Data%20Within%20Cities.ipynb)

## Installation

You can install Spatial Summarize Within using pip:

```bash
pip install spatial_summarize_within
```
Spatial Summarize Within has the following dependencies, which will be installed automatically:

* `geopandas`
* `pandas`
* `shapely`
* `mapclassifier`

## Usage
To use Spatial Summarize Within you'll first need to import the summarize_within function:
```
import spatial_summarize_within as sw
```
## Functions

### sum_within
the `sum_within` function calculates the area of intersection between each polygon in the input shapefile and the summary features, computes the percentage overlap, calculates a weighted sum for specified columns based on the overlap, and finally merges the results back into the original shapefile, returning a geodataframe with the summary statistics.

```
input_shapefile = gpd.read_file("path/to/your/input_shapefile.shp")
overlay_shapefile = gpd.read_file("path/to/your/overlay_shapefile.shp")

sum_result = sw.sum_within(
    input_shapefile=input_shapefile,
    input_summary_features=overlay_shapefile,
    columns=[
        # List the columns you want to sum, e.g.:
        "column1",
        "column2",
        "column3",
    ],
    key="your_group_by_key"
)

```
The result variable will contain a GeoDataFrame with the summarized data.

### mean_within
The `mean_within` function calculates the intersection area between each polygon in the input shapefile and the summary features, computes the percentage overlap, and then calculates a weighted mean for specified columns based on the intersected area. The function then groups the results by a specified key, calculates the mean by dividing the sum by the total intersected area, and merges these results back into the original shapefile, returning a geodataframe with these mean statistics.
```
input_shapefile = gpd.read_file("path/to/your/input_shapefile.shp")
overlay_shapefile = gpd.read_file("path/to/your/overlay_shapefile.shp")

mean_result = sw.mean_within(
    input_shapefile=input_shapefile,
    input_summary_features=overlay_shapefile,
    columns=[
        # List the columns you want to calculate mean, e.g.:
        "column1",
        "column2",
        "column3",
    ],
    key="your_group_by_key"
)
```

### max_within
The `max_within` function computes the intersection area between each polygon in the input shapefile and the summary features, and calculates the percentage overlap. It then determines a weighted value for specified columns based on this overlap. The function groups the results by a given key and identifies the maximum of these weighted values. These results are then merged back into the original shapefile, producing a geodataframe with these maximum statistics.

```
input_shapefile = gpd.read_file("path/to/your/input_shapefile.shp")
overlay_shapefile = gpd.read_file("path/to/your/overlay_shapefile.shp")

max_result = sw.max_within(
    input_shapefile=input_shapefile,
    input_summary_features=overlay_shapefile,
    columns=[
        # List the columns you want to find maximum value, e.g.:
        "column1",
        "column2",
        "column3",
    ],
    key="your_group_by_key"
)
```

### min_within
The `min_within` function computes the intersection area between each polygon in the input shapefile and the summary features, and calculates the percentage overlap. It then determines a weighted value for specified columns based on this overlap. The function groups the results by a given key and identifies the minimum of these weighted values. These results are then merged back into the original shapefile, producing a geodataframe with these minimum statistics.

```
input_shapefile = gpd.read_file("path/to/your/input_shapefile.shp")
overlay_shapefile = gpd.read_file("path/to/your/overlay_shapefile.shp")

min_result = sw.min_within(
    input_shapefile=input_shapefile,
    input_summary_features=overlay_shapefile,
    columns=[
        # List the columns you want to find minimum value, e.g.:
        "column1",
        "column2",
        "column3",
    ],
    key="your_group_by_key"
)
```

# Examples
Suppose we have a shapefile of census tracts with population data (population, male_population, female_population) and a shapefile of zip code boundaries. We want to calculate summary statistics within each zip code relative to the overlap of census tracts on the zip code bounadries.

The figure and table below explain the statistical calculations of an area layer within a hypothetical boundary. The populations were used to calculate the statistics (Sum, Minimum, Maximum, and mean) for the layer. The statistics are calculated using only the proportion of the area that is within the boundary.

<img src="https://github.com/LandonWall/spatial_summarize_within/assets/45885744/60f56e66-9d6d-4ae9-acff-d7ec9ad0e188" width="800" height="500">


<img src="https://github.com/LandonWall/spatial_summarize_within/assets/45885744/2bab81d8-0e2e-4791-a3d3-065d6d33f188" width="650" height="550">

## Code Implementation: 

```
import spatial_summarize_within as sw
import geopandas as gpd
```

```
census_shp = gpd.read_file("path/to/your/census_tracts.shp")
zipcodes_shp = gpd.read_file("path/to/your/zip_codes.shp")
```

### sum_within

```
sum_result = sw.sum_within(
    input_shapefile=input_shapefile,
    input_summary_features=overlay_shapefile,
    columns=[
        "population",
        "male_population",
        "female_population",
    ],
    key="zip_code"
)
```
### mean_within

```
mean_result = sw.mean_within(
    input_shapefile=input_shapefile,
    input_summary_features=overlay_shapefile,
    columns=[
        "population",
        "male_population",
        "female_population",
    ],
    key="zip_code"
)
```
### max_within

```
max_result = sw.max_within(
    input_shapefile=input_shapefile,
    input_summary_features=overlay_shapefile,
    columns=[
        "population",
        "male_population",
        "female_population",
    ],
    key="zip_code"
)
```
### min_within

```
min_result = sw.min_within(
    input_shapefile=input_shapefile,
    input_summary_features=overlay_shapefile,
    columns=[
        "population",
        "male_population",
        "female_population",
    ],
    key="zip_code"
)
```
