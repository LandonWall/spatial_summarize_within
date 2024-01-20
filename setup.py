from setuptools import setup, find_packages

setup(
    name="spatial_summarize_within",
    version="1.0.6",
    Author = "Kenneth Landon Wall",
    Email = "kennethlandonwall@gmail.com",
    packages=find_packages(),
    install_requires=[
        "geopandas",
        "pandas",
    ],
)