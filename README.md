# Manga Downloader

A Python-based tool for downloading manga chapters from "**https://www.mangaread.org**" and converting them to PDF format, optimised for e-readers like Kindle Scribe. The tool features automatic portrait page combining and comprehensive logging.

## Features

- Download manga chapters from mangaread.org
- Convert manga pages to PDF format optimised for e-readers
- Smart portrait page handling:
  - Combines adjacent portrait pages side by side
  - Automatically resizes single portrait pages
  - Maintains optimal dimensions for Kindle Scribe (3048 × 2160 pixels)
- Configurable chapter range downloading
- Comprehensive logging system with rotation
- Automatic cleanup of temporary files
- Robust retry mechanism for failed downloads
- Progress tracking with download status bar

## Requirements

- Python 3.8 or higher
- See `requirements.txt` for package dependencies

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd manga-downloader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Download all chapters starting from chapter 1:
```bash
python downloader.py <manga-name> --start 1
```

### Advanced Usage

Download specific chapter range:
```bash
python downloader.py <manga-name> --start 1 --end 10
```

Enable portrait page combining (recommended for e-readers):
```bash
python downloader.py <manga-name> --rotate
```

Set custom logging level:
```bash
python downloader.py <manga-name> --log-level DEBUG
```

### Example Commands

```bash
# Download One Piece chapters 1-10
python downloader.py one-piece --start 1 --end 10

# Download Naruto with e-reader optimisation
python downloader.py naruto --rotate

# Download Bleach with debug logging
python downloader.py bleach --log-level DEBUG
```

## Project Structure

```
manga-downloader/
├── config/
│ └── device_config.json # Device-specific configurations
├── src/
│ ├── download_handler.py # Manages chapter downloads
│ ├── pdf_handler.py # Handles PDF creation and optimisation
│ └── utils.py # Utility functions and logging setup
├── downloads/ # Downloaded manga storage
├── logs/ # Log files directory
├── requirements.txt # Project dependencies
├── README.md # Project documentation
└── downloader.py # Main script
```

## Logging System

- Logs are stored in the `logs` directory
- Each manga gets its own log file: `<manga_name>.log`
- Log rotation: 5 backup files, 10MB size limit
- Both console and file logging with formatted output
- Configurable log levels: DEBUG, INFO, WARNING, ERROR

## E-Reader Optimisation

The PDF handler includes specific optimisations for e-readers:
- Combines adjacent portrait pages for better reading experience
- Maintains consistent dimensions for Kindle Scribe
- Adds padding and centres images for optimal viewing
- Preserves image quality while ensuring reasonable file sizes

## Device Configuration

The tool supports multiple e-reader devices through the `config/device_config.json` file

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This tool is for educational purposes only. Please respect copyright laws and terms of service of the websites you access. Download only content you have the right to access.

## TODO

- Allow device type selection
