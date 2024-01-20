# Import libraries
import pandas as pd
import geopandas as gpd

# Function
def min_within(input_shapefile, input_summary_features, columns, key, join_type='inner'):
    """
    This function calculates the weighted minimum of the specified columns within the input_shapefile
    boundaries based on the overlapping areas with the input_summary_features, optimized for performance.

    Parameters:
    - input_shapefile (GeoDataFrame): The shapefile to summarize within.
    - input_summary_features (GeoDataFrame): The summary features with values to summarize.
    - columns (list): List of column names in input_summary_features to calculate the minimum for.
    - key (str): The key column name on which to join the shapefiles.
    - join_type (str): Type of join to perform ('inner', 'left', etc.).

    Returns:
    - GeoDataFrame: GeoDataFrame with the weighted minimum of specified columns added.
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

    # Precompute the weighted value for each column
    for column in columns:
        intersected[f"{column}_weighted"] = intersected[column] * intersected["overlap_pct"]

    # Group the results by key and calculate weighted minimum
    grouped_result = intersected.groupby(key)[[f"{column}_weighted" for column in columns]].min().reset_index()

    # Rename columns to original
    for column in columns:
        grouped_result = grouped_result.rename(columns={f"{column}_weighted": column})

    # Merge the result with the overlay geodataframe
    result_gdf = input_shapefile.merge(grouped_result, on=key, how=join_type)

    # Round relevant columns to 2 decimal places
    result_gdf[columns] = result_gdf[columns].round(2)

    # Drop 'intersect_area', 'overlap_pct' columns in intersected if not needed anymore
    intersected = intersected.drop(['intersect_area', 'overlap_pct'] + [f"{column}_weighted" for column in columns], axis=1)

    return result_gdf
