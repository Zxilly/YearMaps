from os import path

from setuptools import find_packages, setup

loc = path.abspath(path.dirname(__file__))

with open(loc + "/requirements.txt") as f:
    requirements = f.read().splitlines()

required = []
dependency_links = []

for line in requirements:
    required.append(line)

setup(
    name="yearmaps",
    author="Zxilly",
    author_email="zxilly@outlook.com",
    url="https://github.com/Zxilly/YearMaps",
    license="GPLv3",
    version="0.0.1",
    description="Generate heat map of a year.",
    packages=find_packages(),
    include_package_data=True,
    install_requires=required,
    dependency_links=dependency_links,
    entry_points={
        "console_scripts": ["yearsmap = yearmaps.cli:main"]
    },
)
