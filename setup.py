from os import path

from setuptools import find_packages, setup

loc = path.abspath(path.dirname(__file__))

with open(loc + "/requirements.txt") as f:
    requirements = f.read().splitlines()

required = []
dependency_links = []

for line in requirements:
    required.append(line)

with open("README.md", "r", encoding='UTF-8') as fh:
    long_description = fh.read()

setup(
    name="yearmaps",
    author="Zxilly",
    author_email="zxilly@outlook.com",
    url="https://github.com/Zxilly/YearMaps",
    license="GPLv3",
    license_file="LICENSE",
    version="0.0.3",
    description="Generate heat map of a year.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=required,
    dependency_links=dependency_links,
    entry_points={
        "console_scripts": ["yearmaps = yearmaps.script:main"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Natural Language :: Chinese (Simplified)"
    ],
)
