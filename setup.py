from setuptools import find_packages, setup

from scrapy_wayback_middleware import __version__

with open("README.md", "r") as f:
    long_description = f.read()


setup(
    name="scrapy-wayback-middleware",
    version=__version__,
    license="MIT",
    author="Pat Sier",
    author_email="pat@citybureau.org",
    description=(
        "Scrapy middleware for submitting URLs to the Internet Archive Wayback Machine"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/City-Bureau/scrapy-wayback-middleware",
    packages=find_packages(),
    install_requires=["scrapy"],
    tests_requires=["flake8", "pytest", "isort"],
    python_requires=">=3.5,<4.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Scrapy",
    ],
)
