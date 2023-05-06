from setuptools import setup, find_packages

setup(
    name="spatial_summarize_within",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "geopandas",
        "pandas",
        "shapely",
        "mapclassify",
    ],
)