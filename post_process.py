import argparse
import logging
import os
import re
from src.pdf_handler import PDFHandler
from src.utils import setup_logging


def extract_chapter_number(filename: str) -> int:
    """Extract chapter number from filename."""
    match = re.search(r'chapter_(\d+)', filename, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 0


def main():
    parser = argparse.ArgumentParser(description='Post-process manga PDFs to rotate landscape pages.')
    parser.add_argument('manga_name', type=str, help='Name of the manga directory to process')
    parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        default='INFO', help='Set the logging level.')

    args = parser.parse_args()

    # Setup logging
    log_level = getattr(logging, args.log_level.upper())
    setup_logging(log_level)
    logger = logging.getLogger(__name__)

    # Construct path to manga directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    downloads_dir = os.path.join(script_dir, 'downloads')
    manga_dir = os.path.join(downloads_dir, args.manga_name)

    if not os.path.exists(manga_dir):
        logger.error(f"Manga directory not found: {manga_dir}")
        return

    # Get and sort PDF files
    pdf_files = [f for f in os.listdir(manga_dir) if f.endswith('.pdf')]
    if not pdf_files:
        logger.error(f"No PDF files found in {manga_dir}")
        return

    # Sort files by chapter number
    pdf_files.sort(key=extract_chapter_number)

    logger.info(f"Found {len(pdf_files)} PDF files in {manga_dir}")
    logger.info("Processing files in order:")
    for file in pdf_files:
        logger.info(f"  Chapter {extract_chapter_number(file):03d}: {file}")

    # Create PDF handler and run post-processing
    pdf_handler = PDFHandler()
    try:
        logger.info("Starting post-processing...")
        pdf_handler.post_processing(manga_dir)
        logger.info("Post-processing completed successfully")
    except Exception as e:
        logger.error(f"Error during post-processing: {e}")


if __name__ == "__main__":
    main()