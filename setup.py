import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="spendee",
    version="0.9.9",
    author="Dionyz Lazar",
    author_email="dio@dionysio.com",
    description="Wrapper for the Spendee API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dionysio/spendee",
    download_url="https://github.com/dionysio/spendee/archive/v0.9.9.9.tar.gz",
    packages=setuptools.find_packages(),
    install_requires=['requests'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)