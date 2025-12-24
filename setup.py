from setuptools import setup, find_packages

setup(
    name="ursa-dsp",
    version="0.2.7",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
