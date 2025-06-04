from setuptools import find_packages, setup

# Read the README for long description
with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python-kanka",
    version="2.0.0",
    packages=find_packages(),
    license="MIT",
    author="Erv Walter",
    author_email="erv@ewal.net",
    description="A modern Python client for the Kanka API with full typing support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ervwalter/python-kanka",
    project_urls={
        "Bug Reports": "https://github.com/ervwalter/python-kanka/issues",
        "Source": "https://github.com/ervwalter/python-kanka",
        "Documentation": "https://github.com/ervwalter/python-kanka#readme",
        "Kanka API": "https://kanka.io/en-US/docs/1.0",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment :: Role-Playing",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.23.0",
        "requests_toolbelt>=0.9.1",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
    },
    keywords="kanka api client worldbuilding rpg campaign tabletop",
)
