import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import logging
from typing import Dict, List, Optional, Any
from venice_ai_integration import VeniceAIOpenRouter

class AIEnhancedScraper:
    """
    Enhanced web scraper with Venice AI integration for intelligent content processing.
    """
    
    def __init__(self, venice_api_key: str, delay: float = 1.0):
        self.venice_ai = VeniceAIOpenRouter(venice_api_key)
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.logger = logging.getLogger(__name__)
        
    def intelligent_crawl(self, start_url: str, max_depth: int = 2, context: str = "") -> List[Dict[str, Any]]:
        """
        Crawl website with AI-powered URL prioritization and content analysis.
        
        Args:
            start_url: Starting URL for crawling
            max_depth: Maximum crawling depth
            context: Context for AI to understand what content is valuable
        
        Returns:
            List of scraped and analyzed content
        """
        visited = set()
        results = []
        queue = [(start_url, 0)]
        
        while queue:
            url, depth = queue.pop(0)
            
            if url in visited or depth > max_depth:
                continue
                
            visited.add(url)
            self.logger.info(f"Scraping: {url} (Depth: {depth})")
            
            # Scrape the page
            scraped_data = self.scrape_with_ai_analysis(url)
            if scraped_data:
                results.append(scraped_data)
                
                # Extract links for next level
                if depth < max_depth and 'links' in scraped_data:
                    # Use AI to prioritize which links to follow
                    prioritized_links = self.venice_ai.intelligent_url_prioritization(
                        scraped_data['links'][:50],  # Limit to 50 links
                        context=context
                    )
                    
                    # Add high-priority links to queue
                    for link_data in prioritized_links:
                        if link_data.get('priority_score', 0) >= 6:  # Only follow high-priority links
                            absolute_url = urljoin(url, link_data['url'])
                            queue.append((absolute_url, depth + 1))
            
            time.sleep(self.delay)  # Rate limiting
            
        return results
    
    def scrape_with_ai_analysis(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a URL and enhance the data with AI analysis.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary containing scraped data and AI analysis
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Basic extraction
            title = soup.title.text.strip() if soup.title else "No Title"
            
            # Extract main content (remove script, style, nav, footer)
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
                
            content = soup.body.get_text(separator='\n', strip=True) if soup.body else ""
            
            # Extract links
            links = [link.get('href') for link in soup.find_all('a', href=True)]
            links = [urljoin(url, link) for link in links if link]
            
            # AI-powered content analysis
            ai_analysis = self.venice_ai.analyze_content(content, "extract_key_info")
            
            # AI-powered content transformation
            cleaned_content = self.venice_ai.content_transformation(content, "clean_and_structure")
            
            # AI-powered categorization
            categories = self.venice_ai.analyze_content(content, "categorize")
            
            # AI-powered summary
            summary = self.venice_ai.analyze_content(content, "summarize")
            
            return {
                'url': url,
                'title': title,
                'raw_content': content[:1000],  # Limit raw content
                'cleaned_content': cleaned_content,
                'links': links,
                'ai_analysis': ai_analysis,
                'categories': categories.get('categories', []) if isinstance(categories, dict) else [],
                'summary': summary.get('response', '') if isinstance(summary, dict) else str(summary),
                'scraped_at': time.time(),
                'content_length': len(content),
                'link_count': len(links)
            }
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error scraping {url}: {e}")
            return None

# Example usage
if __name__ == "__main__":
    # Initialize the AI-enhanced scraper
    # You'll need to set your Venice AI API key
    VENICE_API_KEY = "your_venice_ai_api_key_here"
    
    scraper = AIEnhancedScraper(VENICE_API_KEY, delay=2.0)
    
    # Crawl with AI enhancement
    results = scraper.intelligent_crawl(
        "https://example.com",
        max_depth=2,
        context="Looking for product information, pricing, and contact details"
    )
    
    # Print results
    for result in results:
        print(f"\n--- {result['title']} ---")
        print(f"URL: {result['url']}")
        print(f"Summary: {result['summary']}")
        print(f"Categories: {', '.join(result['categories'])}")
        print(f"Key Info: {result['ai_analysis']}")
