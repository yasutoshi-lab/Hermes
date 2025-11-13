"""
HTML Processor Module

Processes HTML content, extracting text, cleaning markup, and converting
to clean Markdown format.
"""

from typing import Dict, List, Optional
import re


class HTMLProcessor:
    """
    Process HTML documents for analysis.

    This processor extracts clean text from HTML, removes scripts/styles,
    and can convert to Markdown format.
    """

    def __init__(self):
        """Initialize HTML processor."""
        pass

    def extract_text(self, html_content: str) -> str:
        """
        Extract plain text from HTML, removing tags and scripts.

        Args:
            html_content: Raw HTML content

        Returns:
            str: Extracted plain text
        """
        try:
            # Try using BeautifulSoup if available
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove script and style elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()

            # Get text
            text = soup.get_text(separator='\n', strip=True)

            # Clean up whitespace
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            text = '\n'.join(lines)

            return text

        except ImportError:
            # Fallback to regex-based extraction
            return self._extract_text_regex(html_content)

    def _extract_text_regex(self, html_content: str) -> str:
        """
        Fallback text extraction using regex (when BeautifulSoup unavailable).

        Args:
            html_content: Raw HTML content

        Returns:
            str: Extracted text
        """
        # Remove script and style tags with content
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_content)

        # Decode HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        text = text.replace('&quot;', '"')

        # Clean up whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)

        return text

    def extract_links(self, html_content: str) -> List[Dict[str, str]]:
        """
        Extract links from HTML.

        Args:
            html_content: Raw HTML content

        Returns:
            List of dicts with 'text' and 'url' keys
        """
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_content, 'html.parser')
            links = []

            for link in soup.find_all('a', href=True):
                links.append({
                    'text': link.get_text(strip=True),
                    'url': link['href']
                })

            return links

        except ImportError:
            # Fallback to regex
            return self._extract_links_regex(html_content)

    def _extract_links_regex(self, html_content: str) -> List[Dict[str, str]]:
        """
        Fallback link extraction using regex.

        Args:
            html_content: Raw HTML content

        Returns:
            List of dicts with 'text' and 'url' keys
        """
        links = []
        # Match <a href="url">text</a>
        pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>'
        matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)

        for url, text in matches:
            clean_text = re.sub(r'<[^>]+>', '', text).strip()
            if clean_text:
                links.append({'text': clean_text, 'url': url})

        return links

    def to_markdown(self, html_content: str) -> str:
        """
        Convert HTML to Markdown format.

        Args:
            html_content: Raw HTML content

        Returns:
            str: Markdown formatted text
        """
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()

            markdown_lines = []

            for element in soup.descendants:
                if element.name == 'h1':
                    markdown_lines.append(f"\n# {element.get_text(strip=True)}\n")
                elif element.name == 'h2':
                    markdown_lines.append(f"\n## {element.get_text(strip=True)}\n")
                elif element.name == 'h3':
                    markdown_lines.append(f"\n### {element.get_text(strip=True)}\n")
                elif element.name == 'p':
                    markdown_lines.append(f"{element.get_text(strip=True)}\n")
                elif element.name == 'a':
                    text = element.get_text(strip=True)
                    href = element.get('href', '')
                    markdown_lines.append(f"[{text}]({href})")
                elif element.name in ['ul', 'ol']:
                    pass  # Handle list items instead
                elif element.name == 'li':
                    markdown_lines.append(f"- {element.get_text(strip=True)}")
                elif element.name == 'code':
                    markdown_lines.append(f"`{element.get_text()}`")
                elif element.name == 'pre':
                    markdown_lines.append(f"\n```\n{element.get_text()}\n```\n")

            markdown = '\n'.join(markdown_lines)

            # Clean up excessive newlines
            markdown = re.sub(r'\n{3,}', '\n\n', markdown)

            return markdown.strip()

        except ImportError:
            # Fallback to simple extraction
            return self.extract_text(html_content)

    def clean_html(self, html_content: str, preserve_links: bool = True) -> str:
        """
        Clean HTML by removing unnecessary elements.

        Args:
            html_content: Raw HTML content
            preserve_links: Whether to preserve links (default: True)

        Returns:
            str: Cleaned HTML or plain text
        """
        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()

            # Remove comments
            from bs4 import Comment
            for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
                comment.extract()

            if preserve_links:
                return str(soup)
            else:
                return self.extract_text(html_content)

        except ImportError:
            return self.extract_text(html_content)
