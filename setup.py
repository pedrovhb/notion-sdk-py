from setuptools import find_packages, setup


def get_description():
    with open("README.md") as file:
        return file.read()


setup(
    name="notion-client",
    version="0.3.0",
    url="https://github.com/ramnes/notion-sdk-py",
    author="Guillaume Gelin",
    author_email="contact@ramnes.eu",
    description="Python client for the official Notion API",
    long_description=get_description(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.7, <4",
    install_requires=[
        "httpx >= 0.15.0, < 0.18.0",
    ],
)
