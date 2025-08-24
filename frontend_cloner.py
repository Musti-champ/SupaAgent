import requests
import json
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from venice_ai_integration import VeniceAIOpenRouter
import logging

class FrontendCloner:
    """
    Advanced frontend cloning system that can analyze and recreate any frontend
    using modern frameworks and best practices.
    """
    
    def __init__(self, venice_ai: VeniceAIOpenRouter):
        self.venice_ai = venice_ai
        self.logger = logging.getLogger(__name__)
    
    def clone_frontend_from_url(self, url: str, target_framework: str = "react") -> Dict[str, str]:
        """
        Clone a frontend from a live URL and convert to specified framework.
        """
        try:
            # Scrape the website
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract website structure and content
            website_analysis = self._analyze_website_structure(soup, url)
            
            # Generate framework-specific code
            frontend_code = self._generate_frontend_code(website_analysis, target_framework)
            
            return frontend_code
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to clone frontend from {url}: {e}")
            return {"error": f"Failed to clone frontend: {e}"}
    
    def _analyze_website_structure(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """
        Analyze website structure, components, and styling.
        """
        analysis = {
            "title": soup.title.text if soup.title else "Untitled",
            "meta_description": "",
            "layout_structure": {},
            "components": [],
            "styling": {},
            "scripts": [],
            "images": [],
            "forms": [],
            "navigation": {},
            "content_sections": []
        }
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            analysis["meta_description"] = meta_desc.get('content', '')
        
        # Analyze layout structure
        analysis["layout_structure"] = self._extract_layout_structure(soup)
        
        # Extract components
        analysis["components"] = self._identify_components(soup)
        
        # Extract styling information
        analysis["styling"] = self._extract_styling_info(soup)
        
        # Extract navigation
        analysis["navigation"] = self._extract_navigation(soup)
        
        # Extract forms
        analysis["forms"] = self._extract_forms(soup)
        
        # Extract content sections
        analysis["content_sections"] = self._extract_content_sections(soup)
        
        return analysis
    
    def _extract_layout_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract the overall layout structure."""
        structure = {
            "header": None,
            "navigation": None,
            "main_content": None,
            "sidebar": None,
            "footer": None,
            "grid_system": "unknown"
        }
        
        # Identify header
        header = soup.find(['header', 'div'], class_=lambda x: x and 'header' in x.lower() if x else False)
        if header:
            structure["header"] = self._extract_element_info(header)
        
        # Identify navigation
        nav = soup.find(['nav', 'div'], class_=lambda x: x and 'nav' in x.lower() if x else False)
        if nav:
            structure["navigation"] = self._extract_element_info(nav)
        
        # Identify main content
        main = soup.find(['main', 'div'], class_=lambda x: x and any(term in x.lower() for term in ['main', 'content', 'container']) if x else False)
        if main:
            structure["main_content"] = self._extract_element_info(main)
        
        # Identify footer
        footer = soup.find(['footer', 'div'], class_=lambda x: x and 'footer' in x.lower() if x else False)
        if footer:
            structure["footer"] = self._extract_element_info(footer)
        
        return structure
    
    def _identify_components(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Identify reusable components on the page."""
        components = []
        
        # Cards
        cards = soup.find_all(['div', 'article'], class_=lambda x: x and 'card' in x.lower() if x else False)
        for card in cards:
            components.append({
                "type": "card",
                "content": self._extract_element_info(card),
                "styling": self._get_element_styles(card)
            })
        
        # Buttons
        buttons = soup.find_all(['button', 'a'], class_=lambda x: x and any(term in x.lower() for term in ['btn', 'button']) if x else False)
        for button in buttons:
            components.append({
                "type": "button",
                "content": self._extract_element_info(button),
                "styling": self._get_element_styles(button)
            })
        
        # Forms
        forms = soup.find_all('form')
        for form in forms:
            components.append({
                "type": "form",
                "content": self._extract_form_info(form),
                "styling": self._get_element_styles(form)
            })
        
        return components
    
    def _extract_styling_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract styling information from the page."""
        styling = {
            "color_scheme": [],
            "typography": {},
            "layout_system": "unknown",
            "css_frameworks": []
        }
        
        # Extract CSS links
        css_links = soup.find_all('link', rel='stylesheet')
        for link in css_links:
            href = link.get('href', '')
            if 'bootstrap' in href.lower():
                styling["css_frameworks"].append("Bootstrap")
            elif 'tailwind' in href.lower():
                styling["css_frameworks"].append("Tailwind CSS")
            elif 'bulma' in href.lower():
                styling["css_frameworks"].append("Bulma")
        
        # Extract inline styles and classes for color analysis
        all_elements = soup.find_all(True)
        colors = set()
        for element in all_elements[:100]:  # Limit to first 100 elements
            style = element.get('style', '')
            if 'color:' in style or 'background' in style:
                colors.add(style)
        
        styling["color_scheme"] = list(colors)[:10]  # Limit colors
        
        return styling
    
    def _generate_frontend_code(self, analysis: Dict[str, Any], framework: str) -> Dict[str, str]:
        """
        Generate frontend code based on website analysis.
        """
        prompt = f"""
        Generate a complete {framework} application based on this website analysis:
        
        Website Analysis:
        {json.dumps(analysis, indent=2)[:6000]}
        
        Requirements:
        - Recreate the exact layout and design
        - Use modern {framework} best practices
        - Include responsive design
        - Add proper component structure
        - Include styling (CSS modules or styled-components)
        - Add proper state management if needed
        - Include routing if multiple pages detected
        - Make it production-ready
        
        Generate:
        1. Main App component
        2. Individual components for each section
        3. Styling files
        4. Package.json with dependencies
        5. README with setup instructions
        
        Return as structured code blocks with file names.
        """
        
        return self._generate_code_with_ai(prompt, framework)
    
    def _generate_code_with_ai(self, prompt: str, framework: str) -> Dict[str, str]:
        """Generate code using Venice AI."""
        payload = {
            "model": "anthropic/claude-3.5-sonnet",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4000,
            "temperature": 0.3
        }
        
        try:
            response = requests.post(
                f"{self.venice_ai.base_url}/chat/completions",
                headers=self.venice_ai.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            generated_code = result["choices"][0]["message"]["content"]
            
            # Parse the generated code into files
            return self._parse_generated_code(generated_code)
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Code generation error: {e}")
            return {"error": f"Failed to generate code: {e}"}
    
    def _parse_generated_code(self, code: str) -> Dict[str, str]:
        """Parse generated code into separate files."""
        files = {}
        current_file = None
        current_content = []
        
        lines = code.split('\n')
        for line in lines:
            if line.startswith('```') and ('file=' in line or any(ext in line for ext in ['.js', '.jsx', '.ts', '.tsx', '.css', '.json'])):
                if current_file:
                    files[current_file] = '\n'.join(current_content)
                
                # Extract filename
                if 'file=' in line:
                    current_file = line.split('file=')[1].split()[0].strip('"\'')
                else:
                    current_file = "generated_file"
                current_content = []
            elif line.startswith('```') and current_file:
                files[current_file] = '\n'.join(current_content)
                current_file = None
                current_content = []
            elif current_file:
                current_content.append(line)
        
        if current_file and current_content:
            files[current_file] = '\n'.join(current_content)
        
        return files
    
    def _extract_element_info(self, element) -> Dict[str, Any]:
        """Extract information from a DOM element."""
        return {
            "tag": element.name,
            "text": element.get_text(strip=True)[:500],
            "classes": element.get('class', []),
            "attributes": dict(element.attrs),
            "children_count": len(element.find_all())
        }
    
    def _get_element_styles(self, element) -> Dict[str, str]:
        """Extract styling information from an element."""
        return {
            "classes": ' '.join(element.get('class', [])),
            "inline_style": element.get('style', ''),
            "tag": element.name
        }
    
    def _extract_navigation(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract navigation structure."""
        nav_elements = soup.find_all(['nav', 'ul'], class_=lambda x: x and any(term in x.lower() for term in ['nav', 'menu']) if x else False)
        
        navigation = {"items": []}
        for nav in nav_elements:
            links = nav.find_all('a')
            for link in links:
                navigation["items"].append({
                    "text": link.get_text(strip=True),
                    "href": link.get('href', '#'),
                    "classes": link.get('class', [])
                })
        
        return navigation
    
    def _extract_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract form information."""
        forms = []
        for form in soup.find_all('form'):
            form_data = {
                "action": form.get('action', ''),
                "method": form.get('method', 'GET'),
                "fields": []
            }
            
            inputs = form.find_all(['input', 'textarea', 'select'])
            for input_elem in inputs:
                form_data["fields"].append({
                    "type": input_elem.get('type', 'text'),
                    "name": input_elem.get('name', ''),
                    "placeholder": input_elem.get('placeholder', ''),
                    "required": input_elem.has_attr('required')
                })
            
            forms.append(form_data)
        
        return forms
    
    def _extract_content_sections(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract main content sections."""
        sections = []
        
        # Look for semantic sections
        for section in soup.find_all(['section', 'article', 'div'], class_=lambda x: x and any(term in x.lower() for term in ['section', 'content', 'block']) if x else False):
            sections.append({
                "type": "content_section",
                "content": self._extract_element_info(section),
                "styling": self._get_element_styles(section)
            })
        
        return sections[:10]  # Limit to 10 sections
    
    def _extract_form_info(self, form) -> Dict[str, Any]:
        """Extract detailed form information."""
        return {
            "action": form.get('action', ''),
            "method": form.get('method', 'GET'),
            "fields": [self._extract_element_info(field) for field in form.find_all(['input', 'textarea', 'select'])]
        }
