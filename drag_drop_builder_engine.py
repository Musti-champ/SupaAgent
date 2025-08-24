import json
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from venice_ai_integration import VeniceAIOpenRouter
import logging

@dataclass
class BuilderComponent:
    id: str
    type: str
    properties: Dict[str, Any]
    position: Dict[str, float]
    size: Dict[str, float]
    children: List[str] = None

@dataclass
class BuilderProject:
    id: str
    name: str
    description: str
    components: Dict[str, BuilderComponent]
    canvas_settings: Dict[str, Any]
    created_at: str
    updated_at: str

class DragDropBuilderEngine:
    """
    Advanced drag-and-drop builder engine for creating websites, apps, and designs.
    """
    
    def __init__(self, venice_ai: VeniceAIOpenRouter):
        self.venice_ai = venice_ai
        self.logger = logging.getLogger(__name__)
        self.component_library = self._initialize_component_library()
        self.templates = self._initialize_templates()
    
    def _initialize_component_library(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive component library."""
        return {
            # Basic Components
            "text": {
                "name": "Text",
                "category": "basic",
                "properties": {
                    "content": "Sample Text",
                    "fontSize": 16,
                    "fontFamily": "Arial",
                    "color": "#000000",
                    "fontWeight": "normal",
                    "textAlign": "left"
                },
                "icon": "📝"
            },
            "button": {
                "name": "Button",
                "category": "basic",
                "properties": {
                    "text": "Click Me",
                    "backgroundColor": "#007bff",
                    "color": "#ffffff",
                    "borderRadius": 4,
                    "padding": "10px 20px",
                    "onClick": ""
                },
                "icon": "🔘"
            },
            "image": {
                "name": "Image",
                "category": "media",
                "properties": {
                    "src": "/placeholder.jpg",
                    "alt": "Image",
                    "width": 200,
                    "height": 150,
                    "objectFit": "cover"
                },
                "icon": "🖼️"
            },
            "video": {
                "name": "Video",
                "category": "media",
                "properties": {
                    "src": "/placeholder.mp4",
                    "controls": True,
                    "autoplay": False,
                    "loop": False,
                    "width": 400,
                    "height": 300
                },
                "icon": "🎥"
            },
            
            # Form Components
            "input": {
                "name": "Input Field",
                "category": "forms",
                "properties": {
                    "type": "text",
                    "placeholder": "Enter text...",
                    "required": False,
                    "name": "input_field",
                    "value": ""
                },
                "icon": "📝"
            },
            "textarea": {
                "name": "Text Area",
                "category": "forms",
                "properties": {
                    "placeholder": "Enter message...",
                    "rows": 4,
                    "cols": 50,
                    "required": False,
                    "name": "textarea_field"
                },
                "icon": "📄"
            },
            "select": {
                "name": "Dropdown",
                "category": "forms",
                "properties": {
                    "options": ["Option 1", "Option 2", "Option 3"],
                    "defaultValue": "",
                    "required": False,
                    "name": "select_field"
                },
                "icon": "📋"
            },
            "checkbox": {
                "name": "Checkbox",
                "category": "forms",
                "properties": {
                    "label": "Check me",
                    "checked": False,
                    "required": False,
                    "name": "checkbox_field"
                },
                "icon": "☑️"
            },
            
            # Layout Components
            "container": {
                "name": "Container",
                "category": "layout",
                "properties": {
                    "backgroundColor": "transparent",
                    "padding": "20px",
                    "margin": "0px",
                    "borderRadius": 0,
                    "border": "none"
                },
                "icon": "📦"
            },
            "grid": {
                "name": "Grid Layout",
                "category": "layout",
                "properties": {
                    "columns": 3,
                    "gap": "20px",
                    "gridTemplateColumns": "1fr 1fr 1fr"
                },
                "icon": "⚏"
            },
            "flexbox": {
                "name": "Flex Container",
                "category": "layout",
                "properties": {
                    "flexDirection": "row",
                    "justifyContent": "flex-start",
                    "alignItems": "stretch",
                    "gap": "10px"
                },
                "icon": "📐"
            },
            
            # Navigation Components
            "navbar": {
                "name": "Navigation Bar",
                "category": "navigation",
                "properties": {
                    "brand": "Brand",
                    "links": ["Home", "About", "Contact"],
                    "backgroundColor": "#ffffff",
                    "textColor": "#000000"
                },
                "icon": "🧭"
            },
            "menu": {
                "name": "Menu",
                "category": "navigation",
                "properties": {
                    "items": ["Item 1", "Item 2", "Item 3"],
                    "orientation": "horizontal",
                    "style": "default"
                },
                "icon": "📋"
            },
            
            # E-commerce Components
            "product_card": {
                "name": "Product Card",
                "category": "ecommerce",
                "properties": {
                    "title": "Product Name",
                    "price": "$99.99",
                    "image": "/product.jpg",
                    "description": "Product description",
                    "buttonText": "Add to Cart"
                },
                "icon": "🛍️"
            },
            "shopping_cart": {
                "name": "Shopping Cart",
                "category": "ecommerce",
                "properties": {
                    "items": [],
                    "total": 0,
                    "currency": "USD"
                },
                "icon": "🛒"
            },
            
            # Advanced Components
            "chart": {
                "name": "Chart",
                "category": "data",
                "properties": {
                    "type": "bar",
                    "data": [10, 20, 30, 40],
                    "labels": ["A", "B", "C", "D"],
                    "colors": ["#ff6384", "#36a2eb", "#cc65fe", "#ffce56"]
                },
                "icon": "📊"
            },
            "map": {
                "name": "Map",
                "category": "location",
                "properties": {
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "zoom": 10,
                    "markers": []
                },
                "icon": "🗺️"
            },
            "calendar": {
                "name": "Calendar",
                "category": "date",
                "properties": {
                    "defaultDate": "today",
                    "events": [],
                    "view": "month"
                },
                "icon": "📅"
            }
        }
    
    def _initialize_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize template library."""
        return {
            "landing_page": {
                "name": "Landing Page",
                "category": "website",
                "description": "Modern landing page with hero section, features, and CTA",
                "preview": "/templates/landing_page.jpg",
                "components": ["navbar", "hero_section", "features", "cta", "footer"]
            },
            "blog": {
                "name": "Blog Layout",
                "category": "website", 
                "description": "Clean blog layout with sidebar and post grid",
                "preview": "/templates/blog.jpg",
                "components": ["navbar", "blog_header", "post_grid", "sidebar", "footer"]
            },
            "ecommerce": {
                "name": "E-commerce Store",
                "category": "website",
                "description": "Complete online store with product catalog and cart",
                "preview": "/templates/ecommerce.jpg",
                "components": ["navbar", "product_grid", "shopping_cart", "checkout", "footer"]
            },
            "portfolio": {
                "name": "Portfolio",
                "category": "website",
                "description": "Creative portfolio showcase for designers and developers",
                "preview": "/templates/portfolio.jpg",
                "components": ["navbar", "hero", "portfolio_grid", "about", "contact"]
            },
            "dashboard": {
                "name": "Admin Dashboard",
                "category": "app",
                "description": "Data-rich admin dashboard with charts and tables",
                "preview": "/templates/dashboard.jpg",
                "components": ["sidebar", "header", "stats_cards", "charts", "data_table"]
            },
            "social_media_post": {
                "name": "Social Media Post",
                "category": "design",
                "description": "Instagram/Facebook post template with text and images",
                "preview": "/templates/social_post.jpg",
                "components": ["background", "text_overlay", "image", "logo"]
            },
            "email_newsletter": {
                "name": "Email Newsletter",
                "category": "email",
                "description": "Responsive email template for newsletters",
                "preview": "/templates/newsletter.jpg",
                "components": ["header", "content_blocks", "cta_button", "footer"]
            }
        }
    
    def create_project(self, name: str, description: str, template: Optional[str] = None) -> BuilderProject:
        """Create a new builder project."""
        project_id = str(uuid.uuid4())
        
        components = {}
        canvas_settings = {
            "width": 1200,
            "height": 800,
            "backgroundColor": "#ffffff",
            "gridSize": 10,
            "snapToGrid": True
        }
        
        # If template is specified, load template components
        if template and template in self.templates:
            components = self._load_template_components(template)
        
        project = BuilderProject(
            id=project_id,
            name=name,
            description=description,
            components=components,
            canvas_settings=canvas_settings,
            created_at="now",
            updated_at="now"
        )
        
        return project
    
    def _load_template_components(self, template_name: str) -> Dict[str, BuilderComponent]:
        """Load components from a template."""
        template = self.templates[template_name]
        components = {}
        
        # Generate components based on template
        for i, component_type in enumerate(template["components"]):
            component_id = str(uuid.uuid4())
            
            if component_type in self.component_library:
                component_config = self.component_library[component_type]
                
                component = BuilderComponent(
                    id=component_id,
                    type=component_type,
                    properties=component_config["properties"].copy(),
                    position={"x": 50, "y": 50 + (i * 100)},
                    size={"width": 300, "height": 100}
                )
                
                components[component_id] = component
        
        return components
    
    def add_component(self, project: BuilderProject, component_type: str, position: Dict[str, float]) -> str:
        """Add a new component to the project."""
        if component_type not in self.component_library:
            raise ValueError(f"Component type '{component_type}' not found")
        
        component_id = str(uuid.uuid4())
        component_config = self.component_library[component_type]
        
        component = BuilderComponent(
            id=component_id,
            type=component_type,
            properties=component_config["properties"].copy(),
            position=position,
            size={"width": 200, "height": 100}
        )
        
        project.components[component_id] = component
        project.updated_at = "now"
        
        return component_id
    
    def update_component(self, project: BuilderProject, component_id: str, updates: Dict[str, Any]) -> bool:
        """Update component properties."""
        if component_id not in project.components:
            return False
        
        component = project.components[component_id]
        
        # Update properties
        if "properties" in updates:
            component.properties.update(updates["properties"])
        
        # Update position
        if "position" in updates:
            component.position.update(updates["position"])
        
        # Update size
        if "size" in updates:
            component.size.update(updates["size"])
        
        project.updated_at = "now"
        return True
    
    def delete_component(self, project: BuilderProject, component_id: str) -> bool:
        """Delete a component from the project."""
        if component_id not in project.components:
            return False
        
        del project.components[component_id]
        project.updated_at = "now"
        return True
    
    def export_to_html(self, project: BuilderProject) -> str:
        """Export project to HTML."""
        html_prompt = f"""
        Convert this drag-and-drop builder project to clean, production-ready HTML/CSS/JavaScript:
        
        Project: {project.name}
        Components: {json.dumps({k: asdict(v) for k, v in project.components.items()}, indent=2)}
        Canvas Settings: {json.dumps(project.canvas_settings, indent=2)}
        
        Generate:
        1. Semantic HTML structure
        2. Modern CSS with responsive design
        3. JavaScript for interactive components
        4. Optimized for performance and accessibility
        5. Cross-browser compatibility
        
        Return complete HTML file with embedded CSS and JavaScript.
        """
        
        html_code = self.venice_ai.analyze_content(html_prompt, "html_export")
        return html_code
    
    def export_to_react(self, project: BuilderProject) -> Dict[str, str]:
        """Export project to React components."""
        react_prompt = f"""
        Convert this drag-and-drop builder project to React components:
        
        Project: {project.name}
        Components: {json.dumps({k: asdict(v) for k, v in project.components.items()}, indent=2)}
        
        Generate:
        1. Main App component
        2. Individual React components for each builder component
        3. CSS modules or styled-components
        4. TypeScript interfaces if applicable
        5. Modern React patterns (hooks, functional components)
        
        Return as separate files with proper imports and exports.
        """
        
        react_code = self.venice_ai.analyze_content(react_prompt, "react_export")
        
        # Parse the response to separate files
        # This would be implemented based on the AI response format
        return {
            "App.tsx": react_code,
            "components/": "// Individual components would be here",
            "styles/": "// CSS modules would be here"
        }
    
    def generate_ai_design(self, prompt: str, design_type: str) -> Dict[str, Any]:
        """Generate design using AI based on user prompt."""
        ai_design_prompt = f"""
        Create a {design_type} design based on this prompt: {prompt}
        
        Generate:
        1. Layout structure and component placement
        2. Color scheme and typography
        3. Component properties and styling
        4. Responsive design considerations
        5. User experience optimizations
        
        Return as builder project format with components and properties.
        """
        
        ai_design = self.venice_ai.analyze_content(ai_design_prompt, "ai_design_generation")
        
        return {
            "design": ai_design,
            "components": self._parse_ai_design_to_components(ai_design),
            "suggestions": self._generate_design_suggestions(prompt, design_type)
        }
    
    def _parse_ai_design_to_components(self, ai_design: str) -> Dict[str, BuilderComponent]:
        """Parse AI-generated design into builder components."""
        # This would parse the AI response and create actual components
        # Implementation would depend on the AI response format
        components = {}
        
        # Placeholder implementation
        component_id = str(uuid.uuid4())
        components[component_id] = BuilderComponent(
            id=component_id,
            type="container",
            properties={"backgroundColor": "#f8f9fa", "padding": "20px"},
            position={"x": 0, "y": 0},
            size={"width": 800, "height": 600}
        )
        
        return components
    
    def _generate_design_suggestions(self, prompt: str, design_type: str) -> List[str]:
        """Generate design improvement suggestions."""
        return [
            "Consider adding more whitespace for better readability",
            "Use consistent color scheme throughout the design",
            "Ensure mobile responsiveness for all components",
            "Add hover effects for better user interaction",
            "Consider accessibility guidelines for color contrast"
        ]
