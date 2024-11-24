import os
import argparse
import sys
import time
import logging
from src.download_handler import MangaDownloader
from src.pdf_handler import PDFHandler
from src.utils import (setup_logging, setup_download_directories, cleanup_temp_directory, cleanup_temp_files)


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
    logger.info(f"Downloads directory: {downloads_dir}")
    logger.info(f"Manga directory: {manga_dir}")

    base_url = f"https://www.mangaread.org/manga/{args.manga_name}/"
    downloader = MangaDownloader(base_url)
    pdf_creator = PDFHandler()

    if not downloader.verify_manga_exists():
        logger.error(f"Manga '{args.manga_name}' not found at {base_url}")
        cleanup_temp_directory(temp_dir)
        sys.exit(1)

    chapter_num = args.start
    successful_downloads = []  # Track successfully downloaded chapters.

    while True:
        if args.end and chapter_num > args.end:
            logger.info(f"Reached specified end chapter {args.end}")
            break

        chapter_url = f"{base_url}chapter-{chapter_num}/"
        logger.info(f"Processing Chapter {chapter_num}...")

        html_content = downloader.get_html_content(chapter_url)
        if not html_content:
            logger.info(f"No more chapters found after chapter {chapter_num - 1}")
            break

        image_paths = downloader.download_chapter_images(html_content, temp_dir)
        if not image_paths:
            logger.warning(f"No images found in chapter {chapter_num}")
            break

        logger.info(f"Found {len(image_paths)} images in chapter {chapter_num}")

        output_path = os.path.join(manga_dir, f'chapter_{chapter_num:03d}.pdf')
        if pdf_creator.create_pdf(image_paths, output_path):
            cleanup_temp_files(image_paths, temp_dir)
            logger.info(f"Successfully created PDF: {output_path}")
            successful_downloads.append(output_path)  # Track successful creation
        else:
            logger.error(f"Failed to create PDF for chapter {chapter_num}")
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
            logger.error(f"Error during post-processing: {e}")
            logger.info("Post-processing failed, but all chapters were downloaded successfully.")

    # Log final summary.
    if successful_downloads:
        logger.info(f"Successfully downloaded {len(successful_downloads)} chapters.")
        logger.info(f"Download completed for chapters {args.start} to {chapter_num - 1}.")
    else:
        logger.warning("No chapters were successfully downloaded.")


if __name__ == "__main__":
    main()
