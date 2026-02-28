from setuptools import setup, find_packages

setup(
    name="social-media-publisher",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "selenium>=4.0.0",
        "webdriver-manager>=3.8.0",
        "pydantic>=2.0.0",
        "Pillow>=9.0.0",
    ],
    author="Joe",
    description="A library for automated social media publishing",
    python_requires=">=3.8",
)
