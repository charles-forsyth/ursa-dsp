from setuptools import setup, find_packages

setup(
    name="ursa-dsp",
    version="0.2.8",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
