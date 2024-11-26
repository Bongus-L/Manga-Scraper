"""
MangaDownloader class for downloading manga chapters.
"""
import os
import time
import logging
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


class MangaDownloader:
    """
    Class for downloading manga jpgs.
    """
    def __init__(self, base_url: str):
        self.session = self._create_session()
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)

    def verify_manga_exists(self) -> bool:
        """Verify if the manga exists at the specified URL."""
        try:
            response = self.session.get(self.base_url)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            self.logger.error("Failed to verify manga: %s.", e)
            return False

    def get_html_content(self, chapter_url: str) -> str:
        """Fetch the HTML content containing chapter images."""
        try:
            response = self.session.get(chapter_url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.logger.error("Error fetching chapter: %s.", e)
            return None

    def download_chapter_images(self, html_content: str, temp_dir: str) -> list[str]:
        """Download all images from a chapter and save them to the temporary directory."""
        def extract_image_elements(html_content: str) -> list:
            """Extract and sort image elements from HTML content."""
            soup = BeautifulSoup(html_content, 'html.parser')
            images = soup.find_all('img', {'class': 'wp-manga-chapter-img'})

            if not images:
                self.logger.warning("No images found in chapter content.")
                return []

            # Sort images by their order attribute or ID.
            return sorted(images, key=lambda x: int(x.get('data-order', x.get('id', '0').split('-')[-1])))

        def download_single_image(img_url: str, file_path: str, retry_count: int = 3) -> str:
            """Download a single image with retry logic."""
            for attempt in range(retry_count):
                try:
                    response = self.session.get(img_url, timeout=30)
                    response.raise_for_status()

                    if 'image' not in response.headers.get('content-type', ''):
                        raise ValueError(f"Invalid content type: {response.headers.get('content-type')}.")

                    with open(file_path, 'wb') as f:
                        f.write(response.content)

                    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                        return file_path

                    raise IOError("File was not written correctly.")

                except Exception as e:
                    self.logger.warning("Attempt %s/%s failed for image %s: %s.", attempt + 1, retry_count, img_url, e)
                    if attempt < retry_count - 1:
                        time.sleep(2 ** attempt)

            self.logger.error("Failed to download image after %s attempts: %s.", retry_count, img_url)
            return ""

        images = extract_image_elements(html_content)
        image_paths = []

        for index, img in enumerate(tqdm(images, desc="Downloading images")):
            img_url = img.get('src', img.get('data-src', '')).strip()
            if not img_url:
                self.logger.warning("No valid URL found for image %s.", index)
                continue

            file_path = os.path.join(temp_dir, f'image-{index:03d}.jpg')
            if downloaded_path := download_single_image(img_url, file_path):
                image_paths.append(downloaded_path)

        if not image_paths:
            self.logger.error("No images were successfully downloaded.")
            return []

        return image_paths

    def _create_session(self) -> requests.Session:
        """Create and configure a requests session with appropriate headers."""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        return session
