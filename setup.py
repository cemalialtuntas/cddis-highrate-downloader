from setuptools import setup, find_packages
import sys
from pathlib import Path

def get_package_data():
    """Returns a dictionary of package data files."""
    data_files = {}
    
    # Platform-specific binary paths
    if sys.platform == "win32":
        bin_path = "bin/win32/CRX2RNX.exe"
    elif sys.platform == "linux":
        bin_path = "bin/linux/CRX2RNX"
    elif sys.platform == "darwin":
        bin_path = "bin/darwin/CRX2RNX"
    else:
        bin_path = None
        
    if bin_path:
        data_files["cddis_downloader"] = [bin_path]
        
    return data_files

setup(
    name="cddis-highrate-downloader",
    version="1.0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "cddis_downloader": ["CRX2RNX.exe", "CRX2RNX"],  # Include both Windows and Unix executables
    },
    install_requires=[
        "python-dotenv",
    ],
    author="Cemali Altuntas",
    author_email="cemali@yildiz.edu.tr",
    description="A Python-based tool to easily bulk-download high-rate GNSS data from NASA's CDDIS archive",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/cemalialtuntas/cddis-highrate-downloader",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "cddis-download=cddis_downloader.downloader:main",
        ],
    },
) 