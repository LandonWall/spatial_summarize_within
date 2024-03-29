# Spatial Summarize Within
Spatial Summarize Within is a Python package designed to simplify the process of summarizing attribute data within overlapping geometries in shapefiles. Given two shapefiles, it calculates the weighted values of specified attributes based on the overlap percentages between the input shapefile and the overlay shapefile. The statistics are calculated using only the proportion of the area that is within the boundary. Importantly, the package ensures spatial accuracy by automatically detecting and converting Coordinate Reference Systems (CRS). Before carrying out calculations, it converts the shapefiles to an Equal Area CRS for accurate area computations, even across large geographic extents.

# Table of Contents
- [Installation](#installation)
- [Use Cases](#use-cases)
  - [Example 1: Bulk Aggregation of 10 Precinct Shapefiles On To Congressional Districts](#example-1-bulk-aggregation-of-10-precinct-shapefiles-on-to-congressional-districts)
  - [Example 2: Legislative Redistricting](#example-2-legislative-redistricting)
  - [Example 3: Overlaying Election Results on to Novel Geometries](#example-3-overlaying-election-results-on-to-novel-geometries)
- [Detailed Usage](#detailed-usage)
- [Functions](#functions)
  - [sum_within](#sum_within)
  - [mean_within](#mean_within)
  - [max_within](#max_within)
  - [min_within](#min_within)
- [How Summarize Within works](#how-summarize-within-works)

# Installation

You can install Spatial Summarize Within using pip:

```bash
pip install spatial_summarize_within
```
Spatial Summarize Within has the following dependencies, which will be installed automatically:

* `geopandas`
* `pandas`
* `shapely`

# Use Cases

## Example 1: Bulk Aggregation of 10 Precinct Shapefiles On To Congressional Districts
**The Problem:**
Precinct-level election results are published per election and per state. When aiming to analyze multiple states at once, or one state over multiple elections, the process is traditionally extremely time-consuming and involves manually aggregating each file individually. Using spatial_summarize_within, you can accelerate the process of analyzing multiple elections, from multiple states, in multiple years by aggregating many shapefiles in a single sequence. 

In this example, we will gather precinct-level election results from 2016 and 2020 in the five states that flipped from Republican to Democrat in the 2020 Presidential Election. We use [Harvard Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/NH5S2I)'s data to ensure a standardized format. We will then aggregate the 2016 data and the 2020 data, and merge it into one file so we can analyze which Congressional Districts saw the biggest shifts towards Democrats from 2016 to 2020.

![image](https://github.com/LandonWall/spatial_summarize_within/assets/45885744/59395043-dbee-4957-ae0e-aa78ddb5c363)




**Import Spatial_Summarize_Within Package**
```python
import spatial_summarize_within as sw
```

**Import Precinct Result Shapefiles**
As we import the 10 precinct shapefiles, we are also filtering the data to the Presidential contest, creating a total vote column, and standardizing the column names.
```python
# set directory
notebook_directory = Path(os.getcwd())

# filenames
filenames = ["az_2016", "az_2020", "ga_2016", "ga_2020", 
             "mi_2016", "mi_2020", "pa_2016", "pa_2020", "wi_2016", "wi_2020"]

# set dictionary to store shapefiles
shapefiles = {}

# Loop through the filenames and load
for filename in filenames:
    notebook_directory = Path(".")
    shapefile_path = notebook_directory / f"../data/spatial/{filename}/{filename}.shp"

    if shapefile_path.exists():
        # Load shp
        df = gpd.read_file(shapefile_path)

        # Convert all column names to uppercase except 'geometry'
        df.columns = [col.upper() if col != 'geometry' else col for col in df.columns]

        # Filter columns
        if "2016" in filename:
            # Select columns that start with "G16PRE" + "PCTNUM" and "geometry"
            cols_to_keep = [col for col in df.columns if col.startswith("G16PRE") or col in ["PCTNUM", "geometry"]]
            df = df[cols_to_keep]

            # create total vote value for 2016
            vote_cols = df.filter(regex='G16PRE').columns
            df['G16PRE_TOTAL'] = df[vote_cols].sum(axis=1)
        elif "2020" in filename:
            # Select columns that start with "G20PRE" + "PCTNUM" and "geometry"
            cols_to_keep = [col for col in df.columns if col.startswith("G20PRE") or col in ["PCTNUM", "geometry"]]
            df = df[cols_to_keep]

            # create total vote value for 2020
            vote_cols = df.filter(regex='G20PRE').columns
            df['G20PRE_TOTAL'] = df[vote_cols].sum(axis=1)

        # Store filtered GeoDataFrame
        shapefiles[filename] = df
    else:
        print(f"File not found: {shapefile_path}")

shapefiles['az_2016'].head()
```

| PCTNUM   |   G16PRERTRU |   G16PREDCLI |   G16PRELJOH |   G16PRE_TOTAL |
|:---------|-------------:|-------------:|-------------:|---------------:|
| AP0002   |          216 |           60 |           13 |            295 |
| AP0003   |          143 |         1387 |           72 |           1685 |
| AP0005   |           93 |          678 |           38 |            862 |
| AP0009   |         1135 |          228 |           44 |           1445 |
| AP0011   |           47 |          589 |           26 |            694 |

<br>

**Import Congressional Districts Shapefile**
```python
shapefile_path = notebook_directory / '../data/spatial/cd_shapefile/USA_118th_Congressional_Districts.shp'
districts_gdf = gpd.read_file(shapefile_path)

districts_gdf = districts_gdf[['STATE_NAME','DISTRICTID', 'CDFIPS', 'geometry']]

flipped_states = ['Arizona', 'Georgia', 'Michigan', 'Pennsylvania', 'Wisconsin']

districts_gdf = districts_gdf[districts_gdf['STATE_NAME'].isin(flipped_states)]
```

**Merge Precinct Results with Congressional Districts**
```python
# Define the list of states and years
states = ['az', 'ga', 'mi', 'pa', 'wi']

state_mapping = {
    'az': 'Arizona',
    'ga': 'Georgia',
    'mi': 'Michigan',
    'pa': 'Pennsylvania',
    'wi': 'Wisconsin'
}

years = ['2016', '2020']

# Initialize an empty dictionary to store the merged results for each state
aggregated_df = {}

# Loop over each state
for state in states:
    # Get congressional district GeoDataFrame
    districts_gdf = state_districts_gdfs[state_mapping[state]]

    # Aggregate 2016 precinct results
    gdf_2016 = shapefiles[f"{state}_2016"]
    result_2016 = sw.sum_within(
        input_shapefile=districts_gdf,
        input_summary_features=gdf_2016,
        columns=["G16PRERTRU", "G16PREDCLI", "G16PRE_TOTAL"],
        key="DISTRICTID",
        join_type='left'
    )

    # Aggregate 2020 precinct results
    gdf_2020 = shapefiles[f"{state}_2020"]
    result_2020 = sw.sum_within(
        input_shapefile=districts_gdf,
        input_summary_features=gdf_2020,
        columns=["G20PRERTRU", "G20PREDBID", "G20PRE_TOTAL"],
        key="DISTRICTID",
        join_type='left'
    )

    # Merge the results for 2016 and 2020
    merged_result = pd.merge(result_2016, result_2020, on=['STATE_NAME', 'DISTRICTID', 'CDFIPS', 'geometry'], how='outer')

    # Replace NaN values with 0
    merged_result.fillna(0, inplace=True)

    # Store merged data in dictionary
    aggregated_df[state] = merged_result

# Concatenate merged GeoDataFrames
aggregated_df = pd.concat(aggregated_df.values())
aggregated_df.reset_index(drop=True, inplace=True)

aggregated_df.tail()
```

| STATE_NAME   |   DISTRICTID |   CDFIPS |   G16PRERTRU |   G16PREDCLI |   G16PRE_TOTAL |   G20PRERTRU |   G20PREDBID |   G20PRE_TOTAL |
|:-------------|-------------:|---------:|-------------:|-------------:|---------------:|-------------:|-------------:|---------------:|
| Wisconsin    |         5504 |        4 |      74653.9 |       241272 |         335021 |      77983.4 |       258995 |         342813 |
| Wisconsin    |         5505 |        5 |     249437   |       137887 |         414089 |     282485   |       176109 |         466061 |
| Wisconsin    |         5506 |        6 |     206492   |       142796 |         375255 |     236686   |       171559 |         415799 |
| Wisconsin    |         5507 |        7 |     214524   |       138537 |         375007 |     250155   |       165808 |         423094 |
| Wisconsin    |         5508 |        8 |     201207   |       138808 |         361474 |     233555   |       169558 |         410023 |


<br>


**Compare top 20 Largest Shifts from 2016 to 2020 in Flipped States**

Now that we have summarized the precinct level election results onto congressional districts we can easily generate Trump's margin in both years by district and quantify the shift in Trump's margin from 2016 to 2020.

![image](https://github.com/LandonWall/spatial_summarize_within/assets/45885744/6beb61e3-d563-4ae1-b210-906eb194656f)


We can see that Georgia's 6th Congressional District had the largest shift torwards the Democratic Presidential Candidate in 2020, with Georgia 7 and Georgia 11 not far behind.



<br>
<br>

## Example 2: Legislative Redistricting
**The Problem:** During the process of redistricting, existing boundaries of legislative districts are redrawn based on new census data. This poses a unique challenge in that historical precinct data often don't perfectly align with these new boundaries. Furthermore, updated precincts that align with the new districts may not be released until months after the districts are finalized.

For this example, let's calculate the results of the 2020 Presidential Election in the new Legislative Districts, and see how the results compare to the old districts. We will do this by using the spatial_summarize_within package to aggregate the Presidential results from a precinct level to the district level. This will provide us with more accurate and timely insights into the partisan nature of these new districts based on historical data, even before the release of new precincts.

![image](https://github.com/LandonWall/spatial_summarize_within/assets/45885744/38cf13ee-3483-4810-81fe-119ab79e9595)

**Import Spatial_Summarize_Within Package**
```python
import spatial_summarize_within as sw
```

**Import Legislative District Shapefiles**
```python
# Old Legislative Districts
old_LD_sf = gpd.read_file("../data/spatial/AZ_LD_2018/tl_2018_04_sldu.shp")

# New Legislative Districts
new_LD_sf = gpd.read_file("../data/spatial/AZ_LD_2022/Approved_Official_Legislative_Map.shp")
```

**Import Precinct Shapefile**
```python
precinct_sf = gpd.read_file("../data/spatial/precincts_2018/az_vtd_2018_new_pima.shp")
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
```python
precinct_sf = precinct_sf.merge(results_2020, on = "PRECINCT")
```
**Summarize Results by Old Legislative District**
```python
sum_old_ld = sw.sum_within(
    input_shapefile=old_LD_sf,
    input_summary_features=precinct_sf,
    columns=[
        "2020_PRESIDENT_REP",
        "2020_PRESIDENT_DEM",
        "2020_PRESIDENT_OTHER",
        "2020_PRESIDENT_TOTAL",
    ],
    key="DISTRICT",
    join_type='left'
)
```

```python
sum_old_ld.head()
```

| DISTRICT                | BIDEN | JORGENSEN | TRUMP | TOTAL_VOTES |
|-------------------------|-------|-----------|-------|-------------|
| 1 | 48,541| 2,061     | 102,121| 152,723    |
| 2 | 53,679| 1,174     | 33,989 | 88,843     |
| 3 | 59,147| 1,138     | 21,416 | 81,701     |
| 4 | 42,368| 1,233     | 32,428 | 76,029     |
| 5 | 26,758| 1,389     | 83,525 | 111,672    |

<br>

**Summarize Results by New Legislative District**
```python
sum_new_ld = sw.sum_within(
    input_shapefile=new_LD_sf,
    input_summary_features=precinct_sf,
    columns=[
        "2020_PRESIDENT_REP",
        "2020_PRESIDENT_DEM",
        "2020_PRESIDENT_OTHER",
        "2020_PRESIDENT_TOTAL",
    ],
    key="DISTRICT",
    join_type='left'
)
```

```python
sum_new_ld.head()
```

| DISTRICT | BIDEN  | JORGENSEN | TRUMP   | TOTAL_VOTES |
|----------|--------|-----------|---------|-------------|
| 1        | 49,773 | 2,095     | 91,634  | 143,501     |
| 2        | 52,539 | 1,965     | 54,397  | 108,901     |
| 3        | 62,934 | 1,480     | 96,610  | 161,024     |
| 4        | 77,112 | 1,839     | 75,789  | 154,741     |
| 5        | 76,073 | 1,733     | 32,483  | 110,289     |

<br>

**Compare New District Lean to Old District Lean**

Now that we have summarized precinct level election results from 2020 on the old legislative districts and the new districts, we can get a better idea of how the districts are changing. 

![image](https://github.com/LandonWall/spatial_summarize_within/assets/45885744/f2e3d2cb-ac91-4c06-a930-ff9dcb4626ce)

We can see that the new legislative districts that took effect in 2022 are less competitive than they were previously, with toss-up districts dropping from 5 to 2.

|                         | Old Districts | New Districts |
|-------------------------|---------------|---------------|
| Median Margin           | 0.4%         | -1.7%        |
| Average Margin          | -3.7%        | -5.0%        |
| Standard Deviation      | 27.3%        | 27.0%        |
| Minimum Margin          | -51.7%       | -51.5%       |
| Maximum Margin          | 50.7%        | 50.8%        |


|                       | Old Districts | New Districts |
|-----------------------|---------------|---------------|
| Safe Republican       | 10            | 9             |
| Likely Republican     | 1             | 1             |
| Lean Republican       | 1             | 4             |
| Toss-Up               | 5             | 2             |
| Lean Democrat         | 1             | 0             |
| Likely Democrat       | 1             | 2             |
| Safe Democrat         | 11            | 12            |


<br>
<br>

## Example 3: Overlaying Election Results on to Novel Geometries
**The Problem:**
Election results are typically broken down by precinct and county, but often other geographies are more useful to contextuilize results. For example, understanding election results within the boundaries of a city, town, school district, zip code, etc., can help to provide a deeper context for the results. However, obtaining this level of detail accurately can be challenging due to uneven overlapping of precincts or non-standard geographical boundaries. Spatial Summarize Within can be used to accurately overlay election results onto novel geometries, providing a clearer understanding of voting patterns within these entities.

Let's illustrate this with the following example where we overlay the 2021 Virginia Governor election results onto the city boundaries within the state of Virginia.

![image](https://github.com/LandonWall/spatial_summarize_within/assets/45885744/f6616dca-255c-4f7d-ad5b-2317a28ddf42)

<br>

**Import Spatial_Summarize_Within Package**
```python
import spatial_summarize_within as sw
```

**Import Virginia City Shapefiles**
```python
# Virginia Cities
city_sf = gpd.read_file("../data/spatial/VA_CITIES/va_cities.shp")
```

**Import 2021 Virginia Governor Election Results**
```python
results_pcts_2021 = gpd.read_file("../data/spatial/2021 results shapefile/va_2021.shp")
results_pcts_2021.head()
```

| PRECINCT       | Youngkin | McAuliffe | Other | geometry |
|----------------|----------|-----------|-------|----------|
| Chincoteague   | 1300     | 712       | 11    |          |
| Atlantic       | 553      | 135       | 3     |          |
| Greenbackville | 909      | 329       | 5     |          |
| New Church     | 561      | 477       | 9     |          |
| Bloxom         | 373      | 142       | 1     |          |


**Summarize Results by City**
```python
results_by_city = sw.sum_within(
    input_shapefile=city_sf,
    input_summary_features=results_pcts_2021,
    columns=[
        'Youngkin', 
        'McAuliffe',
        'Other', 
    ],
    key="CITY_NAME",
    join_type='left'
)
```

```python
results_by_city.head()
```

| CITY_NAME          | Youngkin | McAuliffe | Other   |
|---------------|----------|-----------|---------|
| Virginia Beach| 86939.22 | 73887.13  | 1257.43 |
| Richmond      | 15675.97 | 61762.11  | 2494.58 |
| Alexandria    | 14090.16 | 44102.62  | 452.83  |
| Chesapeake    | 48064.67 | 42885.88  | 712.39  |
| Norfolk       | 18892.18 | 40352.99  | 849.74  |

<br>

**Visualize Election Results by City**

By summarizing the results of the election by city we have added context to the results and can see that unsuprisngly, voters within the proper city boundaries (which are quite small), largely voted for the Democrat. This implies that Youngkin's 2021 success largely came from suburbs and rural areas which we could prove through further analysis.

![image](https://github.com/LandonWall/spatial_summarize_within/assets/45885744/bae07aba-12e2-44d3-b26e-2e1aa20dc7a5)

<br>
<br>


# Detailed Usage

***sw.sum_within(input_shapefile= _None_ , input_summary_features= _None_ , columns= _None_ , key= _None_ ,join_type=_'inner'_ )***

## Parameters:
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

## Coordinate Reference System (CRS) Handling:

**CRS Detection and Conversion**

The package automatically detects the CRS of the input shapefiles. If the two input shapefiles have different CRS, the package converts the CRS of the overlay shapefile to match the CRS of the input shapefile. This is crucial to ensure that the spatial operations are performed in a consistent spatial reference system.

Please note, it is always recommended to use shapefiles that are in a projected coordinate system (rather than a geographic coordinate system) for accurate area calculations. If your input shapefiles are in a geographic coordinate system (like WGS84, EPSG:4326), you might want to reproject them to a suitable projected coordinate system before using them with this package.

**Conversion to Equal Area CRS**

Before performing area calculations and other spatial operations, Spatial Summarize Within internally converts the input shapefiles to an Equal Area CRS. This step ensures that the calculations are accurate, even when dealing with large spatial extents that span multiple degrees of latitude and/or longitude. The conversion to an Equal Area CRS is done behind the scenes and does not modify the original input shapefiles. The results are converted back to the original CRS before being returned by the functions.

This internal conversion to Equal Area CRS is especially important when the input shapefiles cover large geographic extents. For smaller areas, the distortions introduced by non-equal area CRS might not significantly impact the results, but for larger areas, this step ensures that the spatial summaries are as accurate as possible.

<br>

# Functions

### sum_within
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

### mean_within
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

### max_within
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

### min_within
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

