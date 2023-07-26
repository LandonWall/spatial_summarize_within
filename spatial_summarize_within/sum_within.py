# Import libraries
import pandas as pd
import shapely
from shapely import wkt
import shapely.ops
from shapely.geometry import Polygon, MultiPolygon, shape, Point
import geopandas as gpd

# Function
def sum_within(input_shapefile, input_summary_features, columns, key, join_type='inner'):
    # Check if key exists in both dataframes
    if key in input_shapefile.columns and key in input_summary_features.columns:
        # Append suffix to key in input_summary_features if key match
        input_summary_features = input_summary_features.rename(columns={key: key+"_summary"})

    # set same CRS
    if input_summary_features.crs != input_shapefile.crs:
        input_summary_features = input_summary_features.to_crs(input_shapefile.crs)

    # set equal area projection
    equal_area_crs = 'EPSG:6933'
    input_summary_features = input_summary_features.to_crs(equal_area_crs)
    input_shapefile = input_shapefile.to_crs(equal_area_crs)

    # Add area column to input
    input_summary_features["area"] = input_summary_features.geometry.area
    # Intersect the summary features with the input shapefile
    intersected = gpd.overlay(input_summary_features, input_shapefile, how='intersection', keep_geom_type=False)
    # Calculate the area of each polygon in intersect dataframe
    intersected["intersect_area"] = intersected.area
    # Calculate the percentage overlap of each polygon
    intersected["overlap_pct"] = intersected["intersect_area"] / intersected["area"]
    # Create an empty geodataframe to store the results
    result_gdf = gpd.GeoDataFrame()

    # Loop through each polygon in the overlay
    for polygon in input_shapefile.itertuples():
        # Select intersected parts that belong to current polygon
        temp_intersect = intersected.loc[intersected[key] == getattr(polygon, key)]
        # Calculate the weighted sum
        for column in columns:
            temp_intersect.loc[:, column] = temp_intersect[column] * temp_intersect["overlap_pct"]
        # Keep only the relevant columns in the temp_intersect dataframe
        temp_intersect = temp_intersect[[key] + columns + ['intersect_area', 'overlap_pct']]
        # Group the results
        temp_result = temp_intersect.groupby(key).sum(numeric_only=True).reset_index()
        # Append the results to the result gdf
        result_gdf = pd.concat([result_gdf, temp_result], ignore_index=True)

    # Merge the result with the overlay geodataframe
    result_gdf = input_shapefile.merge(result_gdf, on=key, how=join_type)

    # Round relevant columns to 2 decimal places
    result_gdf[columns] = result_gdf[columns].round(2)

    # Remove the area column from input geodataframe
    input_summary_features = input_summary_features.drop("area", axis=1)

    # Drop 'intersect_area', 'overlap_pct' columns
    result_gdf = result_gdf.drop(['intersect_area', 'overlap_pct'], axis=1)

    return result_gdf