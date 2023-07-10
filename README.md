# Spatial Summarize Within
Spatial Summarize Within is a Python package that simplifies the process of summarizing attribute data within overlapping geometries in shapefiles. Given two shapefiles, it calculates the weighted values of specified attributes based on the overlap percentages between the input shapefile and the overlay shapefile. The statistics are calculated using only the proportion of the area that is within the boundary.

## Table of Contents
- [Installation](#installation)
- [Use Cases](#use-cases)
  - [Example 1: Legislative Redistricting](#example-1-legislative-redistricting)
  - [Example 2: Overlaying Election Results on to Novel Geometries](#example-2-overlaying-election-results-on-to-novel-geometries)
- [Detailed Usage](#detailed-usage)
- [Functions](#functions)
  - [sum_within](#sum_within)
  - [mean_within](#mean_within)
  - [max_within](#max_within)
  - [min_within](#min_within)
- [How Summarize Within works](#how-summarize-within-works)

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

## Use Cases
### Example 1: Legislative Redistricting
**The Problem:** During the process of redistricting, existing boundaries of legislative districts are redrawn based on new census data. Spatial Summarize Within can help overlay historical election data from precincts onto the newly defined districts, allowing for increased context on how the district's partisan nature is changing.

For this example, lets calculate the results of the 2020 Presidential Election in the new Legislative Districts, and see how the results compare to the old districts. We will do this by using the spatial_summarize_within package to aggergate the Presidential results from a precinct level to the district level.

![image](https://github.com/LandonWall/spatial_summarize_within/assets/45885744/38cf13ee-3483-4810-81fe-119ab79e9595)

**Import Spatial_Summarize_Within Package**
```python
import spatial_summarize_within as sw
```

**Import Legislative District Shapefiles**
```python
# Old Legislative Districts
old_LD_sf = gpd.read_file("../data/spatial/AZ_LD_2018/tl_2018_04_sldu.shp")
old_LD_sf = old_LD_sf.to_crs("EPSG:3857")

# New Legislative Districts
new_LD_sf = gpd.read_file("../data/spatial/AZ_LD_2022/Approved_Official_Legislative_Map.shp")
new_LD_sf = new_LD_sf.to_crs("EPSG:3857")
```

**Import Precinct Shapefile**
```python
precinct_sf = gpd.read_file("../data/spatial/precincts_2018/az_vtd_2018_new_pima.shp")
precinct_sf = precinct_sf.to_crs("EPSG:3857")
```
**Import Flat Election Results**
```python
results_2020 = pd.read_table(../data/raw/results_2020.csv, sep=",")
results_2020.head()
```
| PRECINCT  | BIDEN | JORGENSEN | TRUMP | TOTAL_VOTES |
|-----------|-------|-----------|-------|-------------|
| MC_ACACIA | 1770  | 61        | 1475  | 3306        |
| MC_ACOMA  | 1029  | 45        | 1788  | 2862        |
| MC_ACUNA  | 1655  | 13        | 328   | 1996        |
| MC_ADOBE  | 875   | 44        | 1192  | 2111        |
| MC_ADORA  | 2853  | 91        | 4067  | 7011        |

**Merge Results with Precinct Shapefile**

**Summarize Results by Old Legislative District**

**Summarize Results by New Legislative District**



### Example 2: Overlaying Election Results on to Novel Geometries
**The Problem:**


Full [Tutorial](https://github.com/LandonWall/summarize_within_example/blob/master/notebooks/Summarize%20Precinct%20Data%20Within%20Cities.ipynb)

## Detailed Usage

***sw.sum_within(input_shapefile= _None_ , input_summary_features= _None_ , columns= _None_ , key= _None_ ,join_type=_'inner'_ )***

### Parameters:
&nbsp;&nbsp;**input_shapefile:** _str, Path to the input shapefile._

&nbsp;&nbsp;**input_summary_features:** _str, Path to the shapefile with features to summarize._

&nbsp;&nbsp;**columns:** _list-like or scalar, optional, default None_

&nbsp;&nbsp;&nbsp;&nbsp;Column or columns containing numeric or integer data to calculate summary statistics from. If none are specified, all numeric columns are used.

&nbsp;&nbsp;**key:** _column, grouper, array, or list of the previous_

&nbsp;&nbsp;&nbsp;&nbsp;If an array is passed, it must be the same length as the data. The list can contain any of the other types (except list). Keys to group by on the resulting GeoDataFrame index.

&nbsp;&nbsp;**join_type:** _str, default 'inner'_
&nbsp;&nbsp;&nbsp;&nbsp;Determines the type of join to perform:  
&nbsp;&nbsp;&nbsp;&nbsp;- 'left': Use keys from left frame only  
&nbsp;&nbsp;&nbsp;&nbsp;- 'right': Use keys from right frame only  
&nbsp;&nbsp;&nbsp;&nbsp;- 'outer': Use union of keys from both frames  
&nbsp;&nbsp;&nbsp;&nbsp;- 'inner': Use intersection of keys from both frames

&nbsp;&nbsp;**Returns:** Geodataframe



## Functions

#### sum_within
the `sum_within` function calculates the area of intersection between each polygon in the input shapefile and the summary features, computes the percentage overlap, calculates a weighted sum for specified columns based on the overlap, and finally merges the results back into the original shapefile, returning a geodataframe with the summary statistics.

```python
sum_result = sw.sum_within(
    input_shapefile=input_shapefile,
    input_summary_features=overlay_shapefile,
    columns=[
        # List the columns you want to sum, e.g.:
        "column1",
        "column2",
        "column3",
    ],
    key="your_group_by_key",
    join_type='left'
)
```

#### mean_within
The `mean_within` function calculates the intersection area between each polygon in the input shapefile and the summary features, computes the percentage overlap, and then calculates a weighted mean for specified columns based on the intersected area. The function then groups the results by a specified key, calculates the mean by dividing the sum by the total intersected area, and merges these results back into the original shapefile, returning a geodataframe with these mean statistics.
```python
mean_result = sw.mean_within(
    input_shapefile=input_shapefile,
    input_summary_features=overlay_shapefile,
    columns=[
        # List the columns you want to calculate mean, e.g.:
        "column1",
        "column2",
        "column3",
    ],
    key="your_group_by_key",
    join_type='left'
)
```

#### max_within
The `max_within` function computes the intersection area between each polygon in the input shapefile and the summary features, and calculates the percentage overlap. It then determines a weighted value for specified columns based on this overlap. The function groups the results by a given key and identifies the maximum of these weighted values. These results are then merged back into the original shapefile, producing a geodataframe with these maximum statistics.

```python
max_result = sw.max_within(
    input_shapefile=input_shapefile,
    input_summary_features=overlay_shapefile,
    columns=[
        # List the columns you want to find maximum value, e.g.:
        "column1",
        "column2",
        "column3",
    ],
    key="your_group_by_key",
    join_type='left'
)
```

#### min_within
The `min_within` function computes the intersection area between each polygon in the input shapefile and the summary features, and calculates the percentage overlap. It then determines a weighted value for specified columns based on this overlap. The function groups the results by a given key and identifies the minimum of these weighted values. These results are then merged back into the original shapefile, producing a geodataframe with these minimum statistics.

```python
min_result = sw.min_within(
    input_shapefile=input_shapefile,
    input_summary_features=overlay_shapefile,
    columns=[
        # List the columns you want to find minimum value, e.g.:
        "column1",
        "column2",
        "column3",
    ],
    key="your_group_by_key",
    join_type='left'
)
```

# How Summarize Within works
Suppose we have a shapefile of census tracts with population data (population, male_population, female_population) and a shapefile of zip code boundaries. We want to calculate summary statistics within each zip code relative to the overlap of census tracts on the zip code bounadries.

The figure and table below explain the statistical calculations of an area layer within a hypothetical boundary. The populations were used to calculate the statistics (Sum, Minimum, Maximum, and mean) for the layer. The statistics are calculated using only the proportion of the area that is within the boundary.

<img width="717" alt="Screenshot 2023-07-01 at 10 08 13 PM" src="https://github.com/LandonWall/spatial_summarize_within/assets/45885744/895e9015-131d-46c7-923e-8f25954c764d">


<img src="https://github.com/LandonWall/spatial_summarize_within/assets/45885744/2bab81d8-0e2e-4791-a3d3-065d6d33f188" width="650" height="550">

