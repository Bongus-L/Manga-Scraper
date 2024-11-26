"""
PDFHandler class for creating and post-processing PDF files.
"""
import os
import logging
import img2pdf


class PDFHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_pdf(self, image_paths: list[str], output_path: str, combine_portraits: bool = True) -> bool:
        """
        Create a PDF file from a list of image files in sequential order.
        Can combine adjacent portrait images side by side if combine_portraits is True.
        Single portrait images are resized to maintain consistency.

        Args:
            image_paths (list[str]): List of paths to image files
            output_path (str): Path where the PDF will be saved
            combine_portraits (bool): If True, combines adjacent portrait images side by side

        Returns:
            bool: True if successful, False otherwise
        """
        if not image_paths:
            self.logger.warning("No images provided for PDF creation.")
            return False

        try:
            from PIL import Image
            import numpy as np
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            def resize_single_portrait(img: Image.Image) -> Image.Image:
                """
                Resize a single portrait image to fit Kindle Scribe dimensions while maintaining aspect ratio.
                Centers the image horizontally on a white background.
                """
                target_width = 3048  # Kindle Scribe width in pixels
                target_height = 2160  # Kindle Scribe height in pixels

                # Calculate new dimensions maintaining aspect ratio
                aspect_ratio = img.height / img.width
                new_width = target_width // 2  # Use half width like in combined mode
                new_height = int(new_width * aspect_ratio)

                # If height exceeds target, scale down based on height
                if new_height > target_height:
                    new_height = target_height
                    new_width = int(target_height / aspect_ratio)

                # Resize the image
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Create new blank image with white background
                result = Image.new('RGB', (target_width, target_height), 'white')

                # Calculate position to center the image
                x = (target_width - new_width) // 2
                y = (target_height - new_height) // 2

                # Paste resized image onto blank canvas
                result.paste(img_resized, (x, y))
                return result

            def combine_portrait_images(img1: Image.Image, img2: Image.Image) -> Image.Image:
                """
                Combine two portrait images side by side, maintaining Kindle Scribe proportions.
                Kindle Scribe: 10.2" × 7.2" at 300 PPI (3048 × 2160 pixels)
                """
                target_width = 3048  # Kindle Scribe width in pixels
                target_height = 2160  # Kindle Scribe height in pixels

                # Calculate the new width for each image (half of target width with some padding)
                single_width = (target_width // 2) - 20  # 10px padding on each side

                # Resize images maintaining aspect ratio
                def resize_portrait(img: Image.Image) -> Image.Image:
                    aspect_ratio = img.height / img.width
                    new_height = int(single_width * aspect_ratio)

                    # If height exceeds target, scale down based on height
                    if new_height > target_height:
                        new_height = target_height
                        new_width = int(target_height / aspect_ratio)
                    else:
                        new_width = single_width

                    return img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Resize both images
                img1_resized = resize_portrait(img1)
                img2_resized = resize_portrait(img2)

                # Create new blank image with white background
                combined = Image.new('RGB', (target_width, target_height), 'white')

                # Calculate vertical positions to center images
                y1 = (target_height - img1_resized.height) // 2
                y2 = (target_height - img2_resized.height) // 2

                # Calculate horizontal positions with padding
                x1 = 10  # Left padding for first image
                x2 = target_width // 2 + 10  # Start second image at midpoint + padding

                # Paste images onto blank canvas
                combined.paste(img1_resized, (x1, y1))
                combined.paste(img2_resized, (x2, y2))

                return combined

            # Process images
            processed_images = []
            i = 0
            while i < len(image_paths):
                try:
                    with Image.open(image_paths[i]) as img1:
                        is_portrait = img1.width < img1.height

                        # Handle portrait images when combining is enabled
                        if combine_portraits and is_portrait:
                            # Check if we have another portrait image to combine with
                            if i + 1 < len(image_paths):
                                with Image.open(image_paths[i + 1]) as img2:
                                    if img2.width < img2.height:
                                        # Combine the two portrait images
                                        combined = combine_portrait_images(img1, img2)
                                        temp_path = f"{output_path}_temp_{i}.jpg"
                                        combined.save(temp_path, "JPEG", quality=95)
                                        with open(temp_path, 'rb') as temp_file:
                                            processed_images.append(temp_file.read())
                                        os.remove(temp_path)
                                        i += 2  # Skip next image since we used it
                                        continue

                            # If we can't combine (no next image or next image is landscape),
                            # handle single portrait image
                            temp_path = f"{output_path}_temp_{i}.jpg"
                            resized = resize_single_portrait(img1)
                            resized.save(temp_path, "JPEG", quality=95)
                            with open(temp_path, 'rb') as temp_file:
                                processed_images.append(temp_file.read())
                            os.remove(temp_path)
                            i += 1
                            continue

                    # Handle landscape or when combining is disabled
                    with open(image_paths[i], 'rb') as img_file:
                        processed_images.append(img_file.read())
                    i += 1

                except Exception as e:
                    self.logger.error("Error processing image %s: %s.", image_paths[i], e)
                    return False

            # Create the PDF
            with open(output_path, 'wb') as pdf_file:
                pdf_file.write(img2pdf.convert(processed_images))
            return True

        except Exception as e:
            self.logger.error("Failed to create PDF: %s.", e)
            return False
