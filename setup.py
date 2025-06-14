import os

from setuptools import find_packages, setup

# Read version from _version.py
version_file = os.path.join("src", "kanka", "_version.py")
version_dict = {}
with open(version_file) as f:
    exec(f.read(), version_dict)
__version__ = version_dict["__version__"]

# Read the README for long description
with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="python-kanka",
    version=__version__,
    package_dir={"": "src"},
    packages=find_packages(where="src"),
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
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Typing :: Typed",
    ],
    python_requires=">=3.9",
    install_requires=[
        "requests==2.32.4",
        "requests_toolbelt==1.0.0",
        "pydantic==2.11.5",
    ],
    extras_require={
        "dev": [
            "pytest==8.4.0",
            "pytest-cov==6.2.1",
            "pytest-mock==3.14.1",
            "black==25.1.0",
            "isort==6.0.1",
            "ruff==0.11.13",
            "mypy==1.16.0",
            "pre-commit==4.2.0",
        ],
    },
    keywords="kanka api client worldbuilding rpg campaign tabletop ttrpg dnd pathfinder",
    package_data={
        "kanka": ["py.typed"],
    },
    include_package_data=True,
    zip_safe=False,  # Required for py.typed
)
