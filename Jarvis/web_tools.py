import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import urllib.parse
import re

class WebTools:
    """Tools for accessing the internet."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }

    def search_internet(self, query: str, num_results: int = 5) -> Dict:
        """
        Search the internet for a query using DuckDuckGo Lite (Scraper).
        Returns a list of results with title and URL.
        """
        try:
            url = "https://lite.duckduckgo.com/lite/"
            data = {"q": query}
            
            response = requests.post(url, data=data, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Extract links
            links = soup.select(".result-link")
            snippets = soup.select(".result-snippet")
            
            for i, link in enumerate(links):
                if len(results) >= num_results:
                    break
                    
                href = link.get('href')
                title = link.get_text()
                
                # specific filtering for DDG ads/interstitials
                if not href or "duckduckgo.com" in href:
                    continue
                    
                snippet = snippets[i].get_text().strip() if i < len(snippets) else ""
                
                results.append({
                    "title": title,
                    "url": href,
                    "description": snippet
                })
                
            return {
                "success": True, 
                "results": results, 
                "count": len(results)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def read_url(self, url: str) -> Dict:
        """
        Read the content of a specific URL.
        Extracts main text content.
        """
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header", "form"]):
                script.decompose()
                
            # Get text
            text = soup.get_text()
            
            # Break into lines and remove leading/trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limit length to avoid Context Window overflow (approx 4000 chars)
            truncated = len(text) > 8000
            content = text[:8000] + ("...\n[Content truncated]" if truncated else "")
            
            return {
                "success": True, 
                "url": url,
                "title": soup.title.string if soup.title else "No Title",
                "content": content,
                "length": len(content)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
