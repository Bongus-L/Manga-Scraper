from bs4 import BeautifulSoup
import os

def extract_manga_urls(html_file_path):
    """Extract manga chapter URLs from HTML file and save to urls.txt."""
    # Read the HTML file.
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # Parse HTML with BeautifulSoup.
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all manga chapter links.
    chapter_links = soup.select('li.wp-manga-chapter a')
    
    # Extract URLs.
    urls = [link['href'] for link in chapter_links]
    
    # Save URLs to urls.txt.
    with open('urls.txt', 'w', encoding='utf-8') as file:
        for url in urls:
            file.write(url + '\n')

__name__ = "__main__"
extract_manga_urls(r"C:\Users\Bong\Downloads\Read NARUTO - manga Online in English.html")
