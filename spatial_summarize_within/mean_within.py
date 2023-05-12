# Import libraries
import pandas as pd
import shapely
from shapely import wkt
import shapely.ops
from shapely.geometry import Polygon, MultiPolygon, shape, Point
import geopandas as gpd
import mapclassify

# Function
def mean_within(input_shapefile, input_summary_features, columns, key):
    # Read input and overlay shapefiles
    input_shapefile = input_shapefile
    input_summary_features = input_summary_features

    # Add area column to input geodataframe
    input_summary_features["area"] = input_summary_features.geometry.area
    # Create an empty geodataframe to store the results
    result_gdf = gpd.GeoDataFrame()

    # Loop through each polygon in the overlay geodataframe
    for index, row in input_shapefile.iterrows():
        # Create a temporary geodataframe with just the current overlay polygon
        temp_overlay = gpd.GeoDataFrame([row], columns=input_shapefile.columns)
        # set crs
        temp_overlay = temp_overlay.set_crs("EPSG:3395")
        # Intersect the input geodataframe with the current overlay polygon
        temp_intersect = gpd.overlay(input, temp_overlay, how='intersection')
        # Calculate the area of each polygon in intersect dataframe
        temp_intersect["intersect_area"] = temp_intersect.area
        # Calculate the percentage overlap of each polygon in the input geodataframe with the current overlay polygon
        temp_intersect["overlap_pct"] = temp_intersect["intersect_area"] / temp_intersect["area"]
        # Calculate the weighted mean
        columns = columns
        for column in columns:
            temp_intersect[column] = (temp_intersect[column] * temp_intersect["overlap_pct"])
        # Keep only the relevant columns in the temp_intersect dataframe
        temp_intersect = temp_intersect[[key] + columns + ['intersect_area', 'overlap_pct']]
        # Group the results and calculate the mean
        temp_result = temp_intersect.groupby(key).mean(numeric_only=True).reset_index()
        # Append the results to the result gdf
        result_gdf = pd.concat([result_gdf, temp_result], ignore_index=True)

    # Merge the result with the overlay geodataframe
    result_gdf = input_shapefile.merge(result_gdf, on=key)

    # Remove the added area column from input geodataframe
    input_summary_features = input.drop("area", axis=1)

    return result_gdf