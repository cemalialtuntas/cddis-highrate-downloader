# cddis-highrate-downloader: CDDIS High-Rate GNSS Data Downloader

A Python-based tool to easily bulk-download high-rate GNSS data from NASA's CDDIS archive. This tool supports downloading, extracting, and converting GNSS data files with various filtering options.


## Features

- Download high-rate GNSS data from CDDIS FTP server
- Support for station-specific downloads
- Date range support (DOY - Day of Year)
- Hour range filtering
- Automatic file extraction (.gz)
- Optional RINEX conversion (CRX to RNX)
- Anonymous FTP access (no credentials needed)
- Smart file handling (skips already downloaded/converted files)
- Robust connection handling with automatic retry mechanism
- Progress tracking and detailed error reporting

## Prerequisites

- Python 3.6 or higher
- CRX2RNX executable (included for Windows, required for RINEX conversion)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/cemalialtuntas/cddis-highrate-downloader.git
cd cddis-highrate-downloader
```

2. Create and activate a virtual environment (recommended):
Windows
```bash
python -m venv venv
venv\Scripts\activate
```
Linux/Mac
```bash
python -m venv venv
source venv/bin/activate
```

3. Install the package:
```bash
pip install -e .
```

## Usage

After installation, you can run the tool using the command:
```bash
cddis-download
```

The tool will prompt you for the following information:

1. **Station Name**: 
   - Enter a specific station code (e.g., "BRST00FRA")
   - Or press Enter for all stations

2. **Year**: 
   - Enter the year (e.g., "2024")

3. **DOY (Day of Year)**:
   - Enter a single day in any format:
     - Single digit (e.g., "1" → processed as "001")
     - Two digits (e.g., "01" → processed as "001")
     - Three digits (e.g., "001")
   - Or enter a range in any format:
     - "1-30" → processed as "001-030"
     - "01-30" → processed as "001-030"
     - "001-030"

4. **Subfolder**:
   - Enter the subfolder name (e.g., "24d" or "24o")

5. **Hour**:
   - Enter a specific hour (e.g., "00")
   - Enter a range (e.g., "00-05")
   - Or press Enter for all hours

6. **File Processing Options**:
   - Extract downloaded files (y/N)
   - Convert to RINEX format (y/N)

### Example Usage

```bash
$ cddis-download
Enter station name (e.g., BRST00FRA) or press Enter for ALL: BRST00FRA
Enter year (e.g., 2024): 2024
Enter DOY (e.g., 001 or 001-030): 001-003
Enter subfolder (e.g., 24d, 24o): 24d
Enter hour (e.g., 00 or 00-05) or press Enter for ALL: 00-03
Extract downloaded files? (y/N): y
Convert to RINEX (.rnx)? (y/N): y
```

## Output Structure

Downloaded and processed files are organized in the following structure:

```bash
downloads/
└── [STATION_NAME]/
    └── [YEAR]/
        └── [DOY]/
            └── [HOUR]/
                ├── original.crx.gz  # If not extracted
                ├── original.crx     # If extracted
                └── original.rnx     # If converted to RINEX
```

## File Formats

- `.gz`: Compressed files from CDDIS
- `.crx`: Hatanaka-compressed RINEX files
- `.rnx`: RINEX observation files (after conversion)

## RINEX Conversion

The tool includes CRX2RNX.exe for Windows users. For other operating systems, ensure you have CRX2RNX installed and accessible in your system PATH.

## Smart File Handling

The tool now includes intelligent file handling features:
- Skips downloading if RINEX (.rnx) file already exists
- Skips downloading if CRX file already exists
- Automatically retries failed downloads
- Resumes interrupted downloads from the last successful point

## Connection Handling

Version 1.0.1 includes improved connection handling:
- Automatic reconnection on connection loss
- Multiple retry attempts with increasing delays
- Timeout settings to prevent hanging connections
- Passive mode support for better compatibility
- Detailed connection status reporting

## Common Issues

1. **FTP Connection Issues**:
   - Ensure you have internet connectivity
   - Check if CDDIS server is accessible
   - The tool will automatically retry on connection failures

2. **RINEX Conversion Errors**:
   - Verify CRX2RNX is properly installed
   - Check file permissions

3. **Invalid Input Formats**:
   - DOY must be between 001-366 (can be entered as 1, 01, or 001)
   - Hours must be between 00-23
   - Use correct station name format

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Cemali Altuntas (cemali@yildiz.edu.tr)

## Acknowledgments

- NASA's CDDIS for providing GNSS data
- RNXCMP for the CRX2RNX tool (Reference: Hatanaka, Y. (2008), A Compression Format and Tools for GNSS Observation Data, Bulletin of the Geospatioal Information Authority of Japan, 55, 21-30. [available at https://www.gsi.go.jp/ENGLISH/Bulletin55.html](https://www.gsi.go.jp/ENGLISH/Bulletin55.html))

## Citation

If you use this tool in your research, please cite:

```bibtex
@software{cddis_highrate_downloader,
    author = {Altuntas, Cemali},
    title = {CDDIS High-Rate GNSS Data Downloader},
    version = {1.0.2},
    year = {2025},
    url = {https://github.com/cemalialtuntas/cddis-highrate-downloader}
}
```
