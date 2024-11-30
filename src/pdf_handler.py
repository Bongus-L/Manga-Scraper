"""
PDFHandler class for creating and post-processing PDF files.
"""
import os
import json
import logging
import img2pdf
from PIL import Image
from typing import Dict


class PDFHandler:
    def __init__(self, device: str = "kindle_scribe"):
        """
        Initialize PDFHandler with device-specific configuration.
        
        Args:
            device: Name of the device configuration to use.
        """
        self.logger = logging.getLogger(__name__)
        self.config = self._load_device_config(device)
        
        # Device dimensions.
        self.TARGET_WIDTH = self.config["width"]  # Device width in pixels.
        self.TARGET_HEIGHT = self.config["height"]  # Device height in pixels.
        # Padding constant.
        self.PADDING = self.config["padding"]  # Base padding in pixels.
        # Image quality settings.
        self.JPEG_QUALITY = self.config["jpeg_quality"]  # JPEG compression quality.

    def _load_device_config(self, device: str) -> Dict:
        """
        Load device configuration from JSON file.
        
        Args:
            device: Name of the device configuration to load.
            
        Returns:
            Dictionary containing device configuration.
            
        Raises:
            FileNotFoundError: If config file doesn't exist.
            KeyError: If device configuration is not found.
        """
        try:
            config_path = os.path.join(os.path.dirname(__file__), "..", "config", "device_config.json")
            with open(config_path, 'r') as f:
                configs = json.load(f)
                
            if device not in configs:
                self.logger.error("Device %s not found in configuration.", device)
                raise KeyError(f"Device {device} not found in configuration.")
                
            return configs[device]
            
        except FileNotFoundError:
            self.logger.error("Device configuration file not found.")
            raise
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON in device configuration file.")
            raise

    def _resize_image(self, img: 'Image.Image', is_single_portrait: bool = False) -> 'Image.Image':
        """
        Resize an image maintaining aspect ratio, optionally centering on a white canvas.
        
        Args:
            img: Image to resize.
            is_single_portrait: If True, uses full width and centers on canvas.
                              If False, uses half width for combined mode.
        
        Returns:
            Resized image, optionally on a white canvas.
        """
        target_width = (self.TARGET_WIDTH // 2) - (self.PADDING * 2)  # Double padding for combined mode.
        center_on_canvas = False

        if is_single_portrait:
            target_width = self.TARGET_WIDTH // 2
            center_on_canvas = True

        # Calculate new dimensions maintaining aspect ratio.
        aspect_ratio = img.height / img.width
        new_height = int(target_width * aspect_ratio)

        # If height exceeds target, scale down based on height.
        if new_height > self.TARGET_HEIGHT:
            new_height = self.TARGET_HEIGHT
            new_width = int(self.TARGET_HEIGHT / aspect_ratio)
        else:
            new_width = target_width

        # Resize the image.
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        if center_on_canvas:
            # Create new blank image with white background.
            result = Image.new('RGB', (self.TARGET_WIDTH, self.TARGET_HEIGHT), 'white')
            # Calculate position to center the image.
            x = (self.TARGET_WIDTH - new_width) // 2
            y = (self.TARGET_HEIGHT - new_height) // 2
            # Paste resized image onto blank canvas.
            result.paste(img_resized, (x, y))
            return result

        return img_resized

    def _combine_portrait_images(self, img1: 'Image.Image', img2: 'Image.Image') -> 'Image.Image':
        """Combine two portrait images side by side."""
        # Create new blank image with white background.
        combined = Image.new('RGB', (self.TARGET_WIDTH, self.TARGET_HEIGHT), 'white')

        # Resize both images.
        img1_resized = self._resize_image(img1)
        img2_resized = self._resize_image(img2)

        # Calculate vertical positions to center images.
        y1 = (self.TARGET_HEIGHT - img1_resized.height) // 2
        y2 = (self.TARGET_HEIGHT - img2_resized.height) // 2

        # Calculate horizontal positions with padding.
        x1 = self.PADDING  # Left padding for first image.
        x2 = self.TARGET_WIDTH // 2 + self.PADDING  # Start second image at midpoint + padding.

        # Paste images onto blank canvas.
        combined.paste(img1_resized, (x1, y1))
        combined.paste(img2_resized, (x2, y2))

        return combined

    def _process_portrait_images(self, img1: 'Image.Image', image_paths: list[str], 
                               i: int, output_path: str) -> tuple[list[bytes], int]:
        """Process portrait images, either combining two or resizing one."""
        processed_images = []
        
        # Check if we can combine with next image.
        if i + 1 < len(image_paths):
            with Image.open(image_paths[i + 1]) as img2:
                if img2.width < img2.height:
                    combined = self._combine_portrait_images(img1, img2)
                    processed_images.append(self._save_temp_image(combined, output_path, i))
                    return processed_images, i + 2 # +2 because we skip the next image.

        # Handle single portrait image.
        resized = self._resize_image(img1, is_single_portrait=True)
        processed_images.append(self._save_temp_image(resized, output_path, i))
        return processed_images, i + 1

    def _save_temp_image(self, img: 'Image.Image', output_path: str, index: int) -> bytes:
        """Save image to temporary file and return its bytes."""
        temp_path = f"{output_path}_temp_{index}.jpg"
        img.save(temp_path, "JPEG", quality=self.JPEG_QUALITY)
        with open(temp_path, 'rb') as temp_file:
            image_bytes = temp_file.read()
        os.remove(temp_path)
        return image_bytes

    def create_pdf(self, image_paths: list[str], output_path: str, combine_portraits: bool = True) -> bool:
        """Create a PDF file from a list of image files in sequential order."""
        if not image_paths:
            self.logger.warning("No images provided for PDF creation.")
            return False

        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            processed_images = []
            i = 0
            while i < len(image_paths):
                try:
                    with Image.open(image_paths[i]) as img:
                        is_portrait = img.width < img.height

                        if combine_portraits and is_portrait:
                            new_images, i = self._process_portrait_images(img, image_paths, i, output_path)
                            processed_images.extend(new_images)
                            continue

                        # Handle landscape or when combining is disabled.
                        with open(image_paths[i], 'rb') as img_file:
                            processed_images.append(img_file.read())
                        i += 1

                except Exception as e:
                    self.logger.error("Error processing image %s: %s.", image_paths[i], e)
                    return False

            # Create the PDF.
            with open(output_path, 'wb') as pdf_file:
                pdf_file.write(img2pdf.convert(processed_images))
            return True

        except Exception as e:
            self.logger.error("Failed to create PDF: %s.", e)
            return False
