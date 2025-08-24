import requests
import json
import os
import subprocess
import tempfile
import shutil
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging
from venice_ai_integration import VeniceAIOpenRouter

class FullstackDeveloper:
    """
    Comprehensive fullstack developer AI that can clone, generate, debug, and rewrite
    any frontend, backend, or fullstack application in one prompt.
    """
    
    def __init__(self, venice_ai: VeniceAIOpenRouter):
        self.venice_ai = venice_ai
        self.logger = logging.getLogger(__name__)
        self.temp_dir = tempfile.mkdtemp()
        
    def clone_options_prompt(self) -> str:
        """
        Interactive prompt for cloning options.
        """
        return """
        🚀 AI Fullstack Developer - Choose Your Development Task:
        
        1. 🎨 Frontend Only - Clone/Generate frontend (React, Vue, Angular, HTML/CSS/JS)
        2. ⚙️  Backend Only - Clone/Generate backend (FastAPI, Django, Express, Flask)
        3. 🔄 Fullstack - Complete application (Frontend + Backend + Database)
        4. 📁 GitHub Clone & Enhance - Clone repo and add features/fix issues
        5. 🐛 Debug & Fix - Analyze and fix code issues
        6. 🔄 Complete Rewrite - Rewrite entire application with modern stack
        7. 💡 Smart Suggestions - Get architectural recommendations
        
        What would you like me to build/fix today?
        """
    
    def analyze_github_repo(self, repo_url: str) -> Dict[str, Any]:
        """
        Clone and analyze a GitHub repository to understand its structure and capabilities.
        """
        try:
            # Extract repo info from URL
            repo_parts = repo_url.replace('https://github.com/', '').split('/')
            owner, repo_name = repo_parts[0], repo_parts[1]
            
            # Clone repository
            clone_path = os.path.join(self.temp_dir, repo_name)
            subprocess.run(['git', 'clone', repo_url, clone_path], check=True, capture_output=True)
            
            # Analyze repository structure
            analysis = self._analyze_codebase_structure(clone_path)
            
            # Use AI to understand the project
            ai_analysis = self.venice_ai.analyze_content(
                json.dumps(analysis), 
                "analyze_codebase"
            )
            
            return {
                "repo_info": {"owner": owner, "name": repo_name, "url": repo_url},
                "structure_analysis": analysis,
                "ai_insights": ai_analysis,
                "clone_path": clone_path
            }
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git clone failed: {e}")
            return {"error": f"Failed to clone repository: {e}"}
    
    def _analyze_codebase_structure(self, path: str) -> Dict[str, Any]:
        """
        Analyze codebase structure to understand technologies and architecture.
        """
        structure = {
            "languages": {},
            "frameworks": [],
            "package_managers": [],
            "config_files": [],
            "directories": [],
            "key_files": []
        }
        
        # Walk through directory structure
        for root, dirs, files in os.walk(path):
            # Skip hidden directories and node_modules
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']
            
            rel_path = os.path.relpath(root, path)
            if rel_path != '.':
                structure["directories"].append(rel_path)
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                
                # Count file types
                if ext:
                    structure["languages"][ext] = structure["languages"].get(ext, 0) + 1
                
                # Identify key files
                key_files = [
                    'package.json', 'requirements.txt', 'Dockerfile', 'docker-compose.yml',
                    'README.md', 'setup.py', 'Cargo.toml', 'go.mod', 'pom.xml'
                ]
                
                if file in key_files:
                    structure["key_files"].append(os.path.relpath(file_path, path))
                    
                    # Read package.json to identify frameworks
                    if file == 'package.json':
                        try:
                            with open(file_path, 'r') as f:
                                package_data = json.load(f)
                                deps = {**package_data.get('dependencies', {}), 
                                       **package_data.get('devDependencies', {})}
                                
                                # Identify frameworks
                                frameworks = {
                                    'react': 'React',
                                    'vue': 'Vue.js',
                                    '@angular/core': 'Angular',
                                    'express': 'Express.js',
                                    'next': 'Next.js',
                                    'nuxt': 'Nuxt.js',
                                    'svelte': 'Svelte'
                                }
                                
                                for dep, framework in frameworks.items():
                                    if dep in deps:
                                        structure["frameworks"].append(framework)
                        except:
                            pass
        
        return structure
    
    def generate_frontend_from_backend(self, backend_code: str, framework: str = "react") -> str:
        """
        Generate frontend code based on backend API structure.
        """
        prompt = f"""
        Analyze this backend code and generate a complete {framework} frontend application:
        
        Requirements:
        - Create components for all API endpoints
        - Include proper state management
        - Add form handling and validation
        - Implement error handling
        - Use modern UI components and styling
        - Include routing if needed
        - Add authentication if backend has auth
        
        Backend Code:
        {backend_code[:8000]}
        
        Generate a complete, production-ready {framework} application with:
        1. Main App component
        2. Individual page/component files
        3. API service layer
        4. Styling (CSS/Tailwind)
        5. Package.json with dependencies
        
        Return as structured code blocks with file names.
        """
        
        return self._generate_code_with_ai(prompt)
    
    def generate_backend_from_frontend(self, frontend_code: str, framework: str = "fastapi") -> str:
        """
        Generate backend code based on frontend requirements.
        """
        prompt = f"""
        Analyze this frontend code and generate a complete {framework} backend application:
        
        Requirements:
        - Create API endpoints for all frontend data needs
        - Include proper data models/schemas
        - Add authentication and authorization
        - Implement CRUD operations
        - Add input validation and error handling
        - Include database integration
        - Add middleware for CORS, logging, etc.
        
        Frontend Code:
        {frontend_code[:8000]}
        
        Generate a complete, production-ready {framework} backend with:
        1. Main application file
        2. API route handlers
        3. Data models
        4. Database configuration
        5. Authentication system
        6. Requirements.txt/package.json
        
        Return as structured code blocks with file names.
        """
        
        return self._generate_code_with_ai(prompt)
    
    def debug_and_fix_code(self, code: str, error_description: str = "") -> Dict[str, Any]:
        """
        Debug and fix code issues using AI analysis.
        """
        prompt = f"""
        Debug and fix this code. Provide:
        1. Issue analysis and root cause
        2. Fixed code with explanations
        3. Best practices recommendations
        4. Testing suggestions
        
        Error Description: {error_description}
        
        Code to Debug:
        {code[:8000]}
        
        Return detailed analysis and fixed code.
        """
        
        debug_result = self._generate_code_with_ai(prompt)
        
        return {
            "analysis": debug_result,
            "suggestions": self._get_improvement_suggestions(code),
            "fixed_code": debug_result
        }
    
    def rewrite_application(self, existing_code: str, target_stack: str, requirements: str = "") -> str:
        """
        Completely rewrite an application with a modern tech stack.
        """
        prompt = f"""
        Completely rewrite this application using modern {target_stack} stack:
        
        Requirements:
        - Use latest best practices and patterns
        - Implement proper architecture (MVC, Clean Architecture, etc.)
        - Add comprehensive error handling
        - Include testing setup
        - Add proper documentation
        - Optimize for performance and scalability
        - {requirements}
        
        Existing Code:
        {existing_code[:8000]}
        
        Target Stack: {target_stack}
        
        Generate a complete, modern, production-ready application with:
        1. Proper project structure
        2. All necessary files and configurations
        3. Dependencies and setup instructions
        4. Documentation and README
        
        Return as structured code blocks with file names.
        """
        
        return self._generate_code_with_ai(prompt)
    
    def generate_fullstack_app(self, description: str, tech_stack: str = "react-fastapi") -> Dict[str, str]:
        """
        Generate a complete fullstack application from description.
        """
        stacks = {
            "react-fastapi": "React frontend with FastAPI backend",
            "vue-django": "Vue.js frontend with Django backend",
            "angular-express": "Angular frontend with Express.js backend",
            "next-prisma": "Next.js fullstack with Prisma ORM",
            "svelte-flask": "Svelte frontend with Flask backend"
        }
        
        stack_description = stacks.get(tech_stack, tech_stack)
        
        prompt = f"""
        Create a complete fullstack application using {stack_description}:
        
        Application Description: {description}
        
        Generate:
        1. Complete frontend application with all components
        2. Complete backend API with all endpoints
        3. Database schema and models
        4. Authentication system
        5. Deployment configuration
        6. Documentation and setup instructions
        
        Requirements:
        - Production-ready code
        - Proper error handling
        - Input validation
        - Security best practices
        - Responsive design
        - API documentation
        - Testing setup
        
        Return as structured code blocks with file names for both frontend and backend.
        """
        
        fullstack_code = self._generate_code_with_ai(prompt)
        
        return {
            "frontend": fullstack_code,
            "backend": fullstack_code,
            "database": fullstack_code,
            "deployment": fullstack_code
        }
    
    def _generate_code_with_ai(self, prompt: str) -> str:
        """
        Generate code using Venice AI with enhanced prompting.
        """
        enhanced_prompt = f"""
        You are an expert fullstack developer. Generate production-ready, well-documented code.
        
        {prompt}
        
        Code Requirements:
        - Follow industry best practices
        - Include comprehensive error handling
        - Add proper comments and documentation
        - Use modern syntax and patterns
        - Ensure security best practices
        - Make code maintainable and scalable
        
        Return complete, working code with file structure.
        """
        
        payload = {
            "model": "anthropic/claude-3.5-sonnet",
            "messages": [{"role": "user", "content": enhanced_prompt}],
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
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Code generation error: {e}")
            return f"Error generating code: {e}"
    
    def _get_improvement_suggestions(self, code: str) -> List[str]:
        """
        Get AI-powered suggestions for code improvements.
        """
        prompt = f"""
        Analyze this code and provide specific improvement suggestions:
        - Performance optimizations
        - Security enhancements
        - Code quality improvements
        - Architecture recommendations
        - Modern best practices
        
        Code:
        {code[:4000]}
        
        Return as a list of actionable suggestions.
        """
        
        suggestions = self.venice_ai.analyze_content(prompt, "code_suggestions")
        return suggestions.get("suggestions", [])
    
    def cleanup(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
