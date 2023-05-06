# Import libraries
import pandas as pd
import shapely
from shapely import wkt
import shapely.ops
from shapely.geometry import Polygon, MultiPolygon, shape, Point
import geopandas as gpd
import mapclassify

# Function
def summarize_within(input_shapefile, overlay_shapefile, columns_to_sum, key_to_group_by):
    # Read input and overlay shapefiles
    input = input_shapefile
    overlay = overlay_shapefile

    # Add area column to input geodataframe
    input["area"] = input.geometry.area
    # Create an empty geodataframe to store the results
    result_gdf = gpd.GeoDataFrame()

    # Loop through each polygon in the overlay geodataframe
    for index, row in overlay.iterrows():
        # Create a temporary geodataframe with just the current overlay polygon
        temp_overlay = gpd.GeoDataFrame([row], columns=overlay.columns)
        # set crs
        temp_overlay = temp_overlay.set_crs("EPSG:3395")
        # Intersect the input geodataframe with the current overlay polygon
        temp_intersect = gpd.overlay(input, temp_overlay, how='intersection')
        # Calculate the area of each polygon in the intersect geodataframe
        temp_intersect["intersect_area"] = temp_intersect.area
        # Calculate the percentage overlap of each polygon in the input geodataframe with the current overlay polygon
        temp_intersect["overlap_pct"] = temp_intersect["intersect_area"] / temp_intersect["area"]
        # Calculate the weighted sum
        columns = columns_to_sum
        for column in columns:
            temp_intersect[column] = (temp_intersect[column] * temp_intersect["overlap_pct"]).round(0)
        # Group the results
        temp_result = temp_intersect.groupby(key_to_group_by).sum(numeric_only=True).reset_index()
        # Append the results to the result gdf
        result_gdf = pd.concat([result_gdf, temp_result], ignore_index=True)

    # Merge the result with the overlay geodataframe
    result_gdf = overlay.merge(result_gdf, on=key_to_group_by)

    # Remove the added area column from input geodataframe
    input = input.drop("area", axis=1)

    return result_gdf