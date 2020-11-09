"""Setup file."""
from os import path

import setuptools

from wolk import __version__

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="wolk-connect",
    version=__version__,
    install_requires=["paho_mqtt>=1.5.1", "requests>=2.18.1"],
    include_package_data=True,
    license="Apache License 2.0",
    author="WolkAbout",
    author_email="info@wolkabout.com",
    description="Python 3 library for connecting to WolkAbout IoT Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["IoT", "WolkAbout", "Internet of Things"],
    url="https://github.com/Wolkabout/WolkConnect-Python",
    test_suite="test",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Topic :: Communications",
        "Topic :: Software Development :: Embedded Systems",
    ],
)
