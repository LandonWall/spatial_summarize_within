# Import libraries
import pandas as pd
import geopandas as gpd

# Function
def mean_within(input_shapefile, input_summary_features, columns, key, join_type='inner'):
    """
    This function calculates the weighted mean of the specified columns within the input_shapefile
    boundaries based on the overlapping areas with the input_summary_features, optimized for performance.

    Parameters:
    - input_shapefile (GeoDataFrame): The shapefile to summarize within.
    - input_summary_features (GeoDataFrame): The summary features with values to summarize.
    - columns (list): List of column names in input_summary_features to calculate the mean for.
    - key (str): The key column name on which to join the shapefiles.
    - join_type (str): Type of join to perform ('inner', 'left', etc.).

    Returns:
    - GeoDataFrame: GeoDataFrame with the weighted mean of specified columns added.
    """

    # Check if key exists in both dataframes and append suffix to key in input_summary_features if key match
    if key in input_shapefile.columns and key in input_summary_features.columns:
        input_summary_features = input_summary_features.rename(columns={key: key+"_summary"})

    # Set same CRS
    if input_summary_features.crs != input_shapefile.crs:
        input_summary_features = input_summary_features.to_crs(input_shapefile.crs)

    # Set equal area projection
    equal_area_crs = 'EPSG:6933'
    input_summary_features = input_summary_features.to_crs(equal_area_crs)
    input_shapefile = input_shapefile.to_crs(equal_area_crs)

    # Add area column to input
    input_summary_features["area"] = input_summary_features.geometry.area
    # Intersect the input geodataframe with the entire overlay shapefile
    intersected = gpd.overlay(input_summary_features, input_shapefile, how='intersection', keep_geom_type=False)
    # Calculate the area of each polygon in intersect dataframe
    intersected["intersect_area"] = intersected.area
    # Calculate the percentage overlap of each polygon
    intersected["overlap_pct"] = intersected["intersect_area"] / intersected["area"]

    # Precompute the weighted sum for each column
    for column in columns:
        intersected[f"{column}_weighted"] = intersected[column] * intersected["intersect_area"]
        intersected[f"{column}_weighted_pct"] = intersected[f"{column}_weighted"] * intersected["overlap_pct"]

    # Group the results by key and calculate weighted sum and total intersected area
    weighted_sums = intersected.groupby(key)[[f"{column}_weighted_pct" for column in columns]].sum()
    total_areas = intersected.groupby(key)["intersect_area"].sum()

    # Calculate the weighted mean for each column
    for column in columns:
        weighted_sums[f"{column}_mean"] = weighted_sums[f"{column}_weighted_pct"] / total_areas

    # Prepare the final result
    result_gdf = input_shapefile.merge(weighted_sums[[f"{column}_mean" for column in columns]], left_on=key, right_index=True, how=join_type)

    # Rename columns to original and round to 2 decimal places
    for column in columns:
        result_gdf = result_gdf.rename(columns={f"{column}_mean": column})
        result_gdf[column] = result_gdf[column].round(2)

    # Drop 'intersect_area', 'overlap_pct' and any other intermediate columns in intersected if not needed anymore
    intersected = intersected.drop(['intersect_area', 'overlap_pct'] + [f"{column}_weighted" for column in columns] + [f"{column}_weighted_pct" for column in columns], axis=1)

    return result_gdf
