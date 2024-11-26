"""
Main script for downloading manga chapters from mangaread.org.
"""
import os
import sys
import time
import logging
from src.download_handler import MangaDownloader
from src.pdf_handler import PDFHandler
from src.utils import (
    setup_logging,
    setup_download_directories,
    cleanup_temp_directory,
    cleanup_temp_files,
    create_parser
)


def main():
    """Main function showing downloader usage."""
    parser = create_parser()
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
        logger.error("Manga '%s' not found at %s.", args.manga_name, base_url)
        cleanup_temp_directory(temp_dir)
        sys.exit(1)

    chapter_num = args.start
    successful_downloads = []  # Track successfully downloaded chapters.

    while True:
        if args.end and chapter_num > args.end:
            logger.info("Reached specified end chapter %s.",args.end)
            break

        chapter_url = f"{base_url}chapter-{chapter_num}/"
        logger.info("Processing Chapter %s...",chapter_num)

        html_content = downloader.get_html_content(chapter_url)
        if not html_content:
            logger.info("No more chapters found after chapter %s.", chapter_num - 1)
            break

        image_paths = downloader.download_chapter_images(html_content, temp_dir)
        if not image_paths:
            logger.warning("No images found in chapter %s.", chapter_num)
            break

        logger.info("Found %s images in chapter %s.", len(image_paths), chapter_num)

        output_path = os.path.join(manga_dir, f'{args.manga_name}_chapter_{chapter_num:03d}.pdf')
        if pdf_creator.create_pdf(image_paths, output_path, args.rotate):
            cleanup_temp_files(image_paths)
            logger.info("Successfully created PDF: %s.", output_path)
            successful_downloads.append(output_path)  # Track successful creation.
        else:
            logger.error("Failed to create PDF for chapter %s.", chapter_num)
            break

        chapter_num += 1
        time.sleep(2)  # Small delay to avoid rate limits.

    # Final cleanup.
    cleanup_temp_directory(temp_dir)

    # Log final summary.
    if successful_downloads:
        logger.info("Successfully downloaded %s chapters.", len(successful_downloads))
        logger.info("Download completed for chapters %s to %s.", args.start, chapter_num - 1)
    else:
        logger.warning("No chapters were successfully downloaded.")


if __name__ == "__main__":
    main()
