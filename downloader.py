"""
Main script for downloading manga chapters from mangaread.org.
"""
import os
import argparse
import sys
import time
import logging
from src.download_handler import MangaDownloader
from src.pdf_handler import PDFHandler
from src.utils import (
    setup_logging, setup_download_directories,
    cleanup_temp_directory, cleanup_temp_files
)


def main():
    parser = argparse.ArgumentParser(description='Download manga chapters from mangaread.org.')
    parser.add_argument('manga_name', type=str, help='Name of the manga as it appears in the URL.')
    parser.add_argument('--start', type=int, help='Starting chapter number (default: 1).', default=1)
    parser.add_argument('--end', type=int, help='Ending chapter number (optional).', default=None)
    parser.add_argument('--rotate', action='store_true', help='Rotate landscape pages to portrait (optional).')
    parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        default='INFO', help='Set the logging level.')

    args = parser.parse_args()

    # Setup logging.
    log_level = getattr(logging, args.log_level.upper())
    setup_logging(log_level)
    logger = logging.getLogger(__name__)

    # Setup directories.
    downloads_dir, manga_dir, temp_dir = setup_download_directories(args.manga_name)
    logger.info("Downloads directory: %s", downloads_dir)
    logger.info("Manga directory: %s", manga_dir)

    # todo: make a config.json instead of hard-coding.
    base_url = f"https://www.mangaread.org/manga/{args.manga_name}/"
    downloader = MangaDownloader(base_url)
    pdf_creator = PDFHandler()

    if not downloader.verify_manga_exists():
        logger.error("Manga '%s' not found at %s", args.manga_name, base_url)
        cleanup_temp_directory(temp_dir)
        sys.exit(1)

    chapter_num = args.start
    successful_downloads = []  # Track successfully downloaded chapters.

    while True:
        if args.end and chapter_num > args.end:
            logger.info("Reached specified end chapter %s",args.end)
            break

        chapter_url = f"{base_url}chapter-{chapter_num}/"
        logger.info("Processing Chapter %s...",chapter_num)

        html_content = downloader.get_html_content(chapter_url)
        if not html_content:
            logger.info("No more chapters found after chapter %s", chapter_num - 1)
            break

        image_paths = downloader.download_chapter_images(html_content, temp_dir)
        if not image_paths:
            logger.warning("No images found in chapter %s", chapter_num)
            break

        logger.info("Found %s images in chapter %s", len(image_paths), chapter_num)

        output_path = os.path.join(manga_dir, f'chapter_{chapter_num:03d}.pdf')
        if pdf_creator.create_pdf(image_paths, output_path):
            cleanup_temp_files(image_paths, temp_dir)
            logger.info("Successfully created PDF: %s", output_path)
            successful_downloads.append(output_path)  # Track successful creation.
        else:
            logger.error("Failed to create PDF for chapter %s", chapter_num)
            break

        chapter_num += 1
        time.sleep(2)  # Small delay to avoid rate limits.

    # Final cleanup.
    cleanup_temp_directory(temp_dir)

    # Apply post-processing only if we have successful downloads and rotation is requested.
    if successful_downloads and args.rotate:
        logger.info("All chapters downloaded. Starting post-processing...")
        try:
            # Give a small delay to ensure all files are properly closed.
            time.sleep(1)
            pdf_creator.post_processing(manga_dir)
            logger.info("Post-processing completed successfully.")
        except Exception as e:
            logger.error("Error during post-processing: %s", e)
            logger.info("Post-processing failed, but all chapters were downloaded successfully.")

    # Log final summary.
    if successful_downloads:
        logger.info("Successfully downloaded %s chapters.", len(successful_downloads))
        logger.info("Download completed for chapters %s to %s)", args.start, chapter_num - 1)
    else:
        logger.warning("No chapters were successfully downloaded.")


if __name__ == "__main__":
    main()
