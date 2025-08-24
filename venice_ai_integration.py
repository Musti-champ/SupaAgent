import requests
import json
from typing import Dict, List, Optional, Any
import logging

class VeniceAIOpenRouter:
    """
    Venice AI OpenRouter integration for enhanced web scraping with AI capabilities.
    Provides uncensored AI analysis for content processing, extraction, and transformation.
    """
    
    def __init__(self, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://your-scraper-app.com",
            "X-Title": "AI Enhanced Web Scraper"
        }
        self.logger = logging.getLogger(__name__)
    
    def analyze_content(self, content: str, analysis_type: str = "extract_key_info") -> Dict[str, Any]:
        """
        Analyze scraped content using Venice AI for intelligent data extraction.
        
        Args:
            content: Raw scraped content
            analysis_type: Type of analysis (extract_key_info, summarize, categorize, etc.)
        
        Returns:
            Dictionary containing AI analysis results
        """
        prompts = {
            "extract_key_info": f"""
            Analyze this web content and extract key information in JSON format:
            - Main topic/subject
            - Key entities (people, organizations, locations)
            - Important dates and numbers
            - Contact information if present
            - Categories/tags that describe the content
            
            Content: {content[:4000]}  # Limit content length
            
            Return only valid JSON.
            """,
            
            "summarize": f"""
            Provide a concise summary of this web content in 2-3 sentences:
            
            Content: {content[:4000]}
            """,
            
            "categorize": f"""
            Categorize this web content into relevant categories. Return as JSON array:
            
            Content: {content[:4000]}
            
            Return format: {{"categories": ["category1", "category2", ...]}}
            """,
            
            "extract_structured_data": f"""
            Extract structured data from this content in JSON format. Look for:
            - Products/services with prices
            - Events with dates and locations
            - Contact details
            - Business information
            - Any structured data present
            
            Content: {content[:4000]}
            
            Return only valid JSON.
            """
        }
        
        prompt = prompts.get(analysis_type, prompts["extract_key_info"])
        
        payload = {
            "model": "anthropic/claude-3.5-sonnet",  # Venice AI uncensored model
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.3
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            
            # Try to parse as JSON if it's structured data
            if analysis_type in ["extract_key_info", "categorize", "extract_structured_data"]:
                try:
                    return json.loads(ai_response)
                except json.JSONDecodeError:
                    return {"raw_response": ai_response, "parsed": False}
            
            return {"response": ai_response}
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Venice AI API error: {e}")
            return {"error": str(e)}
    
    def intelligent_url_prioritization(self, urls: List[str], context: str = "") -> List[Dict[str, Any]]:
        """
        Use AI to prioritize URLs for scraping based on relevance and importance.
        
        Args:
            urls: List of URLs to prioritize
            context: Context about what kind of content is most valuable
        
        Returns:
            List of URLs with priority scores and reasoning
        """
        url_list = "\n".join([f"- {url}" for url in urls[:20]])  # Limit to 20 URLs
        
        prompt = f"""
        Analyze these URLs and prioritize them for web scraping based on:
        - Likely content value and relevance
        - Potential for containing structured data
        - Importance for comprehensive site coverage
        
        Context: {context}
        
        URLs to prioritize:
        {url_list}
        
        Return JSON format:
        {{
            "prioritized_urls": [
                {{
                    "url": "url_here",
                    "priority_score": 1-10,
                    "reasoning": "why this URL is important",
                    "expected_content_type": "product_page|article|contact|etc"
                }}
            ]
        }}
        """
        
        payload = {
            "model": "anthropic/claude-3.5-sonnet",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1500,
            "temperature": 0.4
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            
            try:
                return json.loads(ai_response)["prioritized_urls"]
            except (json.JSONDecodeError, KeyError):
                # Fallback: return original URLs with default priority
                return [{"url": url, "priority_score": 5, "reasoning": "AI analysis failed"} for url in urls]
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"URL prioritization error: {e}")
            return [{"url": url, "priority_score": 5, "reasoning": "AI analysis failed"} for url in urls]
    
    def content_transformation(self, content: str, transformation_type: str = "clean_and_structure") -> str:
        """
        Transform scraped content using AI for better formatting and structure.
        
        Args:
            content: Raw scraped content
            transformation_type: Type of transformation needed
        
        Returns:
            Transformed content
        """
        transformations = {
            "clean_and_structure": f"""
            Clean and structure this web content for better readability:
            - Remove unnecessary whitespace and formatting
            - Organize into logical sections
            - Preserve important information
            - Make it more readable
            
            Content: {content[:4000]}
            """,
            
            "extract_main_content": f"""
            Extract only the main content from this webpage, removing:
            - Navigation menus
            - Advertisements
            - Footer content
            - Sidebar content
            - Keep only the primary article/content
            
            Content: {content[:4000]}
            """,
            
            "markdown_conversion": f"""
            Convert this web content to clean Markdown format:
            - Preserve headings and structure
            - Convert links to markdown format
            - Clean up formatting
            - Remove HTML artifacts
            
            Content: {content[:4000]}
            """
        }
        
        prompt = transformations.get(transformation_type, transformations["clean_and_structure"])
        
        payload = {
            "model": "anthropic/claude-3.5-sonnet",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2000,
            "temperature": 0.2
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Content transformation error: {e}")
            return content  # Return original content if AI fails
