import img2pdf
import os
import logging
import time
from PyPDF2 import PdfReader, PdfWriter
from contextlib import contextmanager


class PDFHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)


    @contextmanager
    def _open_pdf_safely(self, path: str, mode: str = 'rb'):
        """Safely open and close PDF files with proper resource management."""
        file_obj = None
        try:
            file_obj = open(path, mode)
            yield file_obj
        finally:
            if file_obj:
                file_obj.close()


    def create_pdf(self, image_paths: list[str], output_path: str) -> bool:
        """Create a PDF file from a list of image files in sequential order."""
        if not image_paths:
            self.logger.warning("No images provided for PDF creation.")
            return False

        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Read all images first
            image_data = []
            for path in image_paths:
                with open(path, 'rb') as img_file:
                    image_data.append(img_file.read())

            # Then write the PDF
            with open(output_path, 'wb') as pdf_file:
                pdf_file.write(img2pdf.convert(image_data))
            return True
        except Exception as e:
            self.logger.error(f"Failed to create PDF: {e}")
            return False


    @staticmethod
    def post_processing(pdf_dir: str):
        """Post-process PDFs in the specified directory by rotating landscape pages to portrait."""
        logger = logging.getLogger(__name__)
        logger.info(f"Starting post-processing in directory: {pdf_dir}")

        if not os.path.exists(pdf_dir):
            logger.error(f"Directory not found: {pdf_dir}")
            return

        max_retries = 3
        retry_delay = 2

        for filename in os.listdir(pdf_dir):
            if not filename.endswith('.pdf'):
                continue

            pdf_path = os.path.join(pdf_dir, filename)
            temp_path = f"{pdf_path}.temp"

            for attempt in range(max_retries):
                try:
                    # Ensure temp file doesn't exist from previous attempts
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

                    rotated = False
                    reader = None
                    writer = None

                    # Process the PDF
                    with open(pdf_path, 'rb') as pdf_file:
                        reader = PdfReader(pdf_file)
                        writer = PdfWriter()

                        # Process each page
                        for page in reader.pages:
                            width = float(page.mediabox.width)
                            height = float(page.mediabox.height)

                            if width > height:
                                page.rotate(90)
                                rotated = True

                            writer.add_page(page)

                        # Only write if we made changes
                        if rotated:
                            with open(temp_path, 'wb') as output_file:
                                writer.write(output_file)

                    # If we rotated pages, replace the original file
                    if rotated:
                        # Close any remaining file handles
                        if reader:
                            del reader
                        if writer:
                            del writer

                        # Small delay to ensure file handles are released
                        time.sleep(0.5)

                        try:
                            # On Windows, sometimes we need to retry the replace operation
                            for replace_attempt in range(3):
                                try:
                                    os.replace(temp_path, pdf_path)
                                    break
                                except PermissionError:
                                    if replace_attempt < 2:
                                        time.sleep(1)
                                    else:
                                        raise

                            logger.info(f"Rotated landscape pages in: {filename}")
                        except Exception as e:
                            logger.error(f"Failed to replace file {filename}: {e}")
                            # If replace fails, try to clean up temp file
                            if os.path.exists(temp_path):
                                os.remove(temp_path)

                    # If we got here without errors, break the retry loop
                    break

                except Exception as e:
                    logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for {filename}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                    else:
                        logger.error(f"Final error processing {filename}: {e}")

                finally:
                    # Always try to clean up temp file
                    try:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                    except Exception as e:
                        logger.warning(f"Failed to remove temp file {temp_path}: {e}")