import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import logging
import os
import time


class MangaDownloader:
    def __init__(self, base_url: str):
        self.session = self._create_session()
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)

    def _create_session(self):
        """Create and configure a requests session with appropriate headers."""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        return session

    def verify_manga_exists(self) -> bool:
        """Verify if the manga exists at the specified URL."""
        try:
            response = self.session.get(self.base_url)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            self.logger.error(f"Failed to verify manga: {e}")
            return False

    def get_html_content(self, chapter_url: str):
        """Fetch the HTML content containing chapter images."""
        try:
            response = self.session.get(chapter_url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.logger.error(f"Error fetching chapter {chapter_url}: {str(e)}")
            return None

    def ensure_directory_exists(self, directory: str):
        """Ensure the specified directory exists, creating it if necessary."""
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Failed to create directory {directory}: {e}")
            raise

    def download_chapter_images(self, html_content: str, temp_dir: str) -> list[str]:
        """Download all images from a chapter and save them to the temporary directory."""
        # Ensure temp directory exists before starting downloads
        self.ensure_directory_exists(temp_dir)

        soup = BeautifulSoup(html_content, 'html.parser')
        images = soup.find_all('img', {'class': 'wp-manga-chapter-img'})  # Updated selector

        if not images:
            self.logger.warning("No images found in chapter content")
            return []

        # Sort images by their order attribute or ID
        images.sort(key=lambda x: int(x.get('data-order', x.get('id', '0').split('-')[-1])))
        image_paths = []
        retry_count = 3

        for index, img in enumerate(tqdm(images, desc="Downloading images")):
            img_url = img.get('src', img.get('data-src', '')).strip()
            if not img_url:
                self.logger.warning(f"No valid URL found for image {index}")
                continue

            file_path = os.path.join(temp_dir, f'image-{index:03d}.jpg')

            for attempt in range(retry_count):
                try:
                    response = self.session.get(img_url, timeout=30)
                    response.raise_for_status()

                    # Ensure we got valid image data
                    if 'image' not in response.headers.get('content-type', ''):
                        raise ValueError(f"Invalid content type: {response.headers.get('content-type')}")

                    with open(file_path, 'wb') as f:
                        f.write(response.content)

                    # Verify file was written
                    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                        image_paths.append(file_path)
                        break
                    else:
                        raise IOError("File was not written correctly")

                except Exception as e:
                    self.logger.warning(f"Attempt {attempt + 1}/{retry_count} failed for image {img_url}: {e}")
                    if attempt < retry_count - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        self.logger.error(f"Failed to download image after {retry_count} attempts: {img_url}")

        if not image_paths:
            self.logger.error("No images were successfully downloaded")
            return []

        return image_paths
