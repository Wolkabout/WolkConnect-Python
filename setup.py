import setuptools

from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="wolk-connect",
    version="3.3.2",
    install_requires=["paho_mqtt==1.4.0", "python-persistent-queue==1.3.0"],
    include_package_data=True,
    license="Apache License 2.0",
    author="WolkAbout",
    author_email="info@wolkabout.com",
    description="Python 3 library for connecting to WolkAbout IoT Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["IoT", "WolkAbout", "Internet of Things"],
    url="https://github.com/Wolkabout/WolkConnect-Python",
    packages=setuptools.find_packages(),
    classifiers=(
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: OS Independent",
        "Topic :: Internet",
    ),
)
