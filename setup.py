import re
from setuptools import setup, find_packages

VERSIONFILE = "tagpack/_version.py"
verfilestr = open(VERSIONFILE, "rt").read()
match = re.search(r"^__version__ = '(\d\.\d.\d+(\.\d+)?)'",
                  verfilestr,
                  re.MULTILINE)
if match:
    version = match.group(1)
else:
    raise RuntimeError(
        "Unable to find version string in {}.".format(VERSIONFILE))

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="tagpack",
    version=version,
    packages=find_packages(),
    scripts=['bin/tagpack'],
    include_package_data=True,
    author="Bernhard Haslhofer",
    author_email="bernhard.haslhofer@ait.ac.at",
    description="A utility tool for validating and ingesting TagPacks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/graphsense/graphsense-tagpacks",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "requests>=2.23.0",
        "pyyaml>=5.3.1",
        "tabulate>=0.8.7",
        "cassandra-driver>=3.23.0"
    ],
    test_suite="tests"
)
