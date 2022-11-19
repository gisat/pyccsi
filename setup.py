import pathlib
from setuptools import setup
from pyccsi import __version__

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="pyccsi",
    version=__version__,
    description="Python package for request and download data from CCSI ",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/gisat/pyccsi",
    author="Michal Opletal",
    author_email="michal.opletal@gisat.cz",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10"],
    packages=["pyccsi"],
    package_data={'': ['pyproject.toml']},
    include_package_data=True,
    install_requires=[
        'pydantic >= 1.10.2',
        'setuptools >= 58.5.3',
        'requests >= 2.28.1',
        'termcolor >=2.1.0'
    ]
    )
