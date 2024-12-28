"""
Utility functions for manga downloader.
"""
import os
import argparse
import logging
import shutil
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging(log_level: int = logging.INFO, manga_name: str = None):
    """
    Setup logging configuration for both console and file output.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR).
        manga_name: Name of the manga for log file naming.
    """
    # Create logs directory if it doesn't exist.
    root_dir = Path(__file__).parent.parent
    logs_dir = os.path.join(root_dir, 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    # Define log file path with manga name if provided.
    log_filename = f"{manga_name}.log" if manga_name else "manga_downloader.log"
    log_file = os.path.join(logs_dir, log_filename)

    # Create formatters for output styling.
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Setup file handler with rotation.
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB per file.
        backupCount=5,  # Keep 5 backup files.
        encoding='utf-8'  # Ensure proper text encoding.
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(log_level)

    # Setup console handler for terminal output.
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level)

    # Setup root logger with specified level.
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to prevent duplicate logs.
    root_logger.handlers = []

    # Add both handlers to the logger.
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Log the initialisation information.
    logging.info("Logging setup completed successfully.")
    logging.info(f"Log file location: {log_file}.")


def setup_download_directories(manga_name: str) -> tuple[str, str, str]:
    """
    Create necessary directories for downloading manga.

    Returns:
        Tuple containing (downloads_dir, manga_dir, temp_dir).
    """
    def get_download_paths() -> tuple[str, str, str]:
        # Get the project root directory.
        root_dir = Path(__file__).parent.parent

        # Create paths.
        downloads_dir = os.path.join(root_dir, 'downloads')
        manga_dir = os.path.join(downloads_dir, manga_name)
        temp_dir = os.path.join(manga_dir, 'temp')

        return downloads_dir, manga_dir, temp_dir

    downloads_dir, manga_dir, temp_dir = get_download_paths()

    # Create directories.
    os.makedirs(downloads_dir, exist_ok=True)
    os.makedirs(manga_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)

    return downloads_dir, manga_dir, temp_dir


def cleanup_temp_directory(temp_dir: str) -> None:
    """Clean up temporary directory and its contents."""
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except Exception as e:
        logging.error("Failed to clean up temporary directory %s: %s", temp_dir, e)


def cleanup_temp_files( image_paths: list[str]) -> None:
    """Clean up temporary files."""
    for path in image_paths:
        try:
            os.remove(path)
        except Exception as e:
            logging.error("Failed to remove temporary file %s: %s.", path, e)


def create_parser() -> argparse.ArgumentParser:
    """Create and return an ArgumentParser with improved help messages."""
    # TODO: Allow device type arg.
    parser = argparse.ArgumentParser(
        description='Download manga from mangaread.org then convert to PDF.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s one-piece --start 1 --end 10
  %(prog)s naruto --start 50 --rotate
  %(prog)s bleach --log-level DEBUG
        """
    )

    parser.add_argument(
        'manga_name',
        type=str,
        help='Name of the manga as it appears in the URL (e.g., "one-piece", "naruto")'
    )

    parser.add_argument(
        '--start',
        type=int,
        default=1,
        metavar='N',
        help='Starting chapter number (default: %(default)s)'
    )

    parser.add_argument(
        '--end',
        type=int,
        metavar='N',
        help='Ending chapter number (if omitted, downloads until no more chapters found)'
    )

    parser.add_argument(
        '--rotate',
        action='store_true',
        help='Rotate pages to match Kindle Scribe screen size'
    )

    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set the logging level (default: %(default)s)'
    )

    parser.add_argument(
        '--buffer',
        action="store_true",
        help="Add a blank page at the start to shift combined images.",
        default=False
    )

    parser.add_argument(
        '--reverse-img-order',
        action='store_true',
        help='Reverse the order of images when combining portrait pages.',
        default=False
    )

    return parser
