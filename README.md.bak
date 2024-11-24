# Manga Downloader

A Python-based tool for downloading manga chapters from mangaread.org and converting them to PDF format. The tool supports automatic page rotation and includes comprehensive logging.

## Features

- Download manga chapters from mangaread.org
- Convert manga pages to PDF format
- Automatic landscape to portrait page rotation
- Configurable chapter range downloading
- Comprehensive logging system
- Temporary file cleanup
- Retry mechanism for failed downloads
- Progress tracking with tqdm

## Requirements

```
beautifulsoup4
requests
img2pdf
PyPDF2
tqdm
```

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

Download chapters starting from chapter 1:
```bash
python downloader.py <manga-name>
```

### Advanced Usage

Download specific chapter range:
```bash
python downloader.py <manga-name> --start 1 --end 10
```

Download with page rotation enabled:
```bash
python downloader.py <manga-name> --rotate
```

Set custom logging level:
```bash
python downloader.py <manga-name> --log-level DEBUG
```

### Post-Processing

To rotate landscape pages in existing PDFs:
```bash
python post_process.py <manga-name>
```

## Project Structure

```
manga-downloader/
├── src/
│   ├── download_handler.py  # Handles manga page downloads
│   ├── pdf_handler.py       # Manages PDF creation and processing
│   └── utils.py            # Utility functions
├── downloads/              # Downloaded manga storage
├── logs/                  # Log files directory
├── downloader.py          # Main download script
└── post_process.py        # Post-processing script
```

## Log Files

- Log files are stored in the `logs` directory
- Each manga gets its own log file: `<manga_name>.log`
- Log files use rotation with 5 backup files and 10MB size limit

## Error Handling

The tool includes several error handling features:
- Automatic retry for failed downloads
- Comprehensive logging of errors
- Cleanup of temporary files on failure
- Verification of downloaded files
- Safe PDF file handling

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License


## Disclaimer

This tool is for educational purposes only. Please respect copyright laws and terms of service of the websites you access.
