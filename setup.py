from setuptools import setup, find_packages

setup(
    name="spatial_summarize_within",
    version="1.0.5",
    Author = "Kenneth Landon Wall",
    Email = "Landon@AlloyAnalytics.org",
    packages=find_packages(),
    install_requires=[
        "geopandas",
        "pandas",
        "shapely",
    ],
)