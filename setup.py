import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="autodi",
    version="0.1.1",
    author="Jonáš Kulhánek",
    author_email="jonas.kulhanek@live.com",
    description="DI container for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jkulhanek/python-autodi",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)