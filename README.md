# spatial_summarize_within

Use this package to aggregate the data inside of one shapefile on to another shapefile.

The results will be relative to the size of the overlap between geometries. 

MAIN USE:
from geo_summarizer.summarizer import summarize_within

result = summarize_within(
    input_shapefile=input,
    overlay_shapefile=overlay,
    columns_to_sum=[...],
    key_to_group_by="KEY"
)
