from setuptools import setup, find_packages

setup(
    name="ursa-dsp",
    version="0.3.4",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
