"""
Backend Generator - Analyzes frontend code/Figma and generates appropriate backends
"""

import json
import re
import ast
from typing import Dict, List, Any, Optional
import requests
from dataclasses import dataclass
import logging
from pathlib import Path
from config import Config, AIConfig
from venice_ai_integration import VeniceAIOpenRouter

logger = logging.getLogger(__name__)

@dataclass
class BackendSpec:
    """Specification for generated backend"""
    framework: str  # fastapi, django, express, etc.
    database: str   # postgresql, mongodb, sqlite, etc.
    auth_method: str  # jwt, oauth, session, etc.
    apis: List[Dict]  # API endpoints to generate
    models: List[Dict]  # Data models
    middleware: List[str]  # Required middleware
    dependencies: List[str]  # Package dependencies

class FrontendAnalyzer:
    """Analyzes frontend code to determine backend requirements"""
    
    def __init__(self):
        self.venice_ai = VeniceAIOpenRouter()
        self.component_patterns = {
            'react': [r'function\s+(\w+)', r'const\s+(\w+)\s*=.*=>', r'class\s+(\w+)'],
            'vue': [r'<template.*?name="(\w+)"', r'export\s+default\s*{.*?name:\s*["\'](\w+)["\']'],
            'angular': [r'@Component.*?selector:\s*["\'](\w+)["\']']
        }
        
        self.api_patterns = [
            r'fetch\(["\']([^"\']+)["\']',
            r'axios\.(get|post|put|delete)\(["\']([^"\']+)["\']',
            r'api\.[a-zA-Z]+\(["\']([^"\']+)["\']',
        ]
        
        self.auth_patterns = [
            r'login|signin|authenticate',
            r'token|jwt|bearer',
            r'logout|signout',
            r'register|signup'
        ]
    
    def analyze_code(self, code: str, file_type: str = 'auto') -> Dict:
        """Analyze frontend code and extract backend requirements"""
        if file_type == 'auto':
            file_type = self._detect_framework(code)
        
        # Basic analysis
        basic_analysis = {
            'framework': file_type,
            'components': self._extract_components(code, file_type),
            'api_endpoints': self._extract_api_calls(code),
            'auth_requirements': self._detect_auth_needs(code),
            'data_models': self._infer_data_models(code),
            'routing': self._extract_routes(code),
            'state_management': self._detect_state_management(code)
        }
        
        # Enhanced AI analysis using Venice AI
        if Config.AI_ANALYSIS_ENABLED:
            ai_analysis = self.venice_ai.analyze_content(
                f"Analyze this frontend code for backend requirements: {code}",
                analysis_type="backend_requirements"
            )
            basic_analysis['ai_insights'] = ai_analysis
        
        return basic_analysis
    
    def _detect_framework(self, code: str) -> str:
        """Detect the frontend framework"""
        if 'import React' in code or 'from "react"' in code:
            return 'react'
        elif 'Vue' in code or '@vue' in code:
            return 'vue'
        elif '@angular' in code or 'Angular' in code:
            return 'angular'
        elif '<script>' in code and '<style>' in code:
            return 'vanilla'
        return 'unknown'
    
    def _extract_components(self, code: str, framework: str) -> List[str]:
        """Extract component names"""
        components = []
        patterns = self.component_patterns.get(framework, [])
        
        for pattern in patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            components.extend(matches)
        
        return list(set(components))
    
    def _extract_api_calls(self, code: str) -> List[Dict]:
        """Extract API endpoint calls"""
        endpoints = []
        
        for pattern in self.api_patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    method, url = match[0], match[1] if len(match) > 1 else match[0]
                else:
                    method, url = 'GET', match
                
                endpoints.append({
                    'method': method.upper(),
                    'url': url,
                    'inferred_purpose': self._infer_endpoint_purpose(url)
                })
        
        return endpoints
    
    def _detect_auth_needs(self, code: str) -> Dict:
        """Detect authentication requirements"""
        auth_needs = {
            'required': False,
            'methods': [],
            'protected_routes': []
        }
        
        for pattern in self.auth_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                auth_needs['required'] = True
                if 'login' in pattern or 'signin' in pattern:
                    auth_needs['methods'].append('login')
                if 'token' in pattern or 'jwt' in pattern:
                    auth_needs['methods'].append('jwt')
        
        return auth_needs
    
    def _infer_data_models(self, code: str) -> List[Dict]:
        """Infer data models from frontend code"""
        models = []
        
        # Look for TypeScript interfaces or PropTypes
        interface_pattern = r'interface\s+(\w+)\s*{([^}]+)}'
        interfaces = re.findall(interface_pattern, code, re.DOTALL)
        
        for name, fields in interfaces:
            model = {
                'name': name,
                'fields': self._parse_interface_fields(fields)
            }
            models.append(model)
        
        return models
    
    def _extract_routes(self, code: str) -> List[str]:
        """Extract routing information"""
        routes = []
        
        # React Router patterns
        route_patterns = [
            r'<Route.*?path=["\']([^"\']+)["\']',
            r'path:\s*["\']([^"\']+)["\']',
            r'router\.push\(["\']([^"\']+)["\']'
        ]
        
        for pattern in route_patterns:
            matches = re.findall(pattern, code)
            routes.extend(matches)
        
        return list(set(routes))
    
    def _detect_state_management(self, code: str) -> Dict:
        """Detect state management patterns"""
        state_info = {
            'type': 'none',
            'stores': [],
            'actions': []
        }
        
        if 'redux' in code.lower():
            state_info['type'] = 'redux'
        elif 'vuex' in code.lower():
            state_info['type'] = 'vuex'
        elif 'useState' in code:
            state_info['type'] = 'react_hooks'
        
        return state_info
    
    def _infer_endpoint_purpose(self, url: str) -> str:
        """Infer the purpose of an API endpoint"""
        url_lower = url.lower()
        
        if 'user' in url_lower:
            return 'user_management'
        elif 'auth' in url_lower or 'login' in url_lower:
            return 'authentication'
        elif 'product' in url_lower:
            return 'product_management'
        elif 'order' in url_lower:
            return 'order_management'
        else:
            return 'general'
    
    def _parse_interface_fields(self, fields_str: str) -> List[Dict]:
        """Parse TypeScript interface fields"""
        fields = []
        lines = fields_str.strip().split('\n')
        
        for line in lines:
            line = line.strip().rstrip(',;')
            if ':' in line:
                name, type_info = line.split(':', 1)
                fields.append({
                    'name': name.strip(),
                    'type': type_info.strip(),
                    'required': '?' not in name
                })
        
        return fields

class BackendCodeGenerator:
    """Generates backend code based on frontend analysis"""
    
    def __init__(self, ai_model_path: Optional[str] = None):
        self.ai_model_path = ai_model_path
        self.venice_ai = VeniceAIOpenRouter()
        self.templates = self._load_templates()
    
    def generate_backend(self, frontend_analysis: Dict, preferences: Dict = None) -> BackendSpec:
        """Generate complete backend specification"""
        preferences = preferences or {}
        
        # Determine backend framework
        framework = preferences.get('framework', self._suggest_framework(frontend_analysis))
        database = preferences.get('database', self._suggest_database(frontend_analysis))
        
        # Generate API endpoints
        apis = self._generate_apis(frontend_analysis)
        
        # Generate data models
        models = self._generate_models(frontend_analysis)
        
        # Determine middleware needs
        middleware = self._determine_middleware(frontend_analysis)
        
        # Generate dependencies
        dependencies = self._generate_dependencies(framework, database, middleware)
        
        return BackendSpec(
            framework=framework,
            database=database,
            auth_method=self._determine_auth_method(frontend_analysis),
            apis=apis,
            models=models,
            middleware=middleware,
            dependencies=dependencies
        )
    
    def generate_code_files(self, spec: BackendSpec) -> Dict[str, str]:
        """Generate actual code files from specification"""
        files = {}
        
        if spec.framework == 'fastapi':
            files.update(self._generate_fastapi_files(spec))
        elif spec.framework == 'django':
            files.update(self._generate_django_files(spec))
        elif spec.framework == 'express':
            files.update(self._generate_express_files(spec))
        
        return files
    
    def _suggest_framework(self, analysis: Dict) -> str:
        """Suggest backend framework based on frontend analysis"""
        # Use AI to make intelligent suggestions
        if Config.AI_ANALYSIS_ENABLED:
            suggestion = self.venice_ai.analyze_content(
                f"Suggest the best backend framework for this frontend: {json.dumps(analysis)}",
                analysis_type="framework_suggestion"
            )
            if suggestion and 'framework' in suggestion:
                return suggestion['framework']
        
        # Fallback to simple heuristics
        if analysis.get('framework') == 'react':
            return AIConfig.DEFAULT_BACKEND_FRAMEWORK
        elif analysis.get('framework') == 'vue':
            return 'express'
        else:
            return AIConfig.DEFAULT_BACKEND_FRAMEWORK
    
    def _suggest_database(self, analysis: Dict) -> str:
        """Suggest database based on requirements"""
        models = analysis.get('data_models', [])
        
        if len(models) > 5 or any('relationship' in str(model) for model in models):
            return AIConfig.DEFAULT_DATABASE
        else:
            return 'sqlite'
    
    def _generate_apis(self, analysis: Dict) -> List[Dict]:
        """Generate API endpoint specifications"""
        apis = []
        
        for endpoint in analysis.get('api_endpoints', []):
            api_spec = {
                'path': endpoint['url'],
                'method': endpoint['method'],
                'purpose': endpoint['inferred_purpose'],
                'parameters': self._infer_parameters(endpoint),
                'response_model': self._infer_response_model(endpoint)
            }
            apis.append(api_spec)
        
        # Add authentication endpoints if needed
        if analysis.get('auth_requirements', {}).get('required'):
            apis.extend([
                {'path': '/auth/login', 'method': 'POST', 'purpose': 'authentication'},
                {'path': '/auth/register', 'method': 'POST', 'purpose': 'authentication'},
                {'path': '/auth/logout', 'method': 'POST', 'purpose': 'authentication'}
            ])
        
        return apis
    
    def _generate_models(self, analysis: Dict) -> List[Dict]:
        """Generate data model specifications"""
        models = []
        
        for model_info in analysis.get('data_models', []):
            model = {
                'name': model_info['name'],
                'fields': model_info['fields'],
                'relationships': self._infer_relationships(model_info)
            }
            models.append(model)
        
        # Add User model if authentication is required
        if analysis.get('auth_requirements', {}).get('required'):
            models.append({
                'name': 'User',
                'fields': [
                    {'name': 'id', 'type': 'int', 'primary_key': True},
                    {'name': 'email', 'type': 'str', 'unique': True},
                    {'name': 'password_hash', 'type': 'str'},
                    {'name': 'created_at', 'type': 'datetime'}
                ]
            })
        
        return models
    
    def _load_templates(self) -> Dict:
        """Load code generation templates"""
        return {
            'fastapi': {
                'main': '''
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

{endpoints}
''',
                'model': '''
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class {model_name}(Base):
    __tablename__ = "{table_name}"
    
{fields}
''',
            }
        }
    
    def _generate_fastapi_files(self, spec: BackendSpec) -> Dict[str, str]:
        """Generate FastAPI project files"""
        files = {}
        
        # Generate main.py
        endpoints_code = []
        for api in spec.apis:
            endpoint_code = self._generate_fastapi_endpoint(api)
            endpoints_code.append(endpoint_code)
        
        files['main.py'] = self.templates['fastapi']['main'].format(
            endpoints='\n\n'.join(endpoints_code)
        )
        
        # Generate models.py
        models_code = []
        for model in spec.models:
            model_code = self._generate_fastapi_model(model)
            models_code.append(model_code)
        
        files['models.py'] = '\n\n'.join(models_code)
        
        return files
    
    def _generate_fastapi_endpoint(self, api: Dict) -> str:
        """Generate FastAPI endpoint code"""
        method = api['method'].lower()
        path = api['path']
        function_name = self._path_to_function_name(path, method)
        
        return f'''
@app.{method}("{path}")
async def {function_name}():
    # TODO: Implement {api['purpose']} logic
    return {{"message": "Endpoint implemented"}}
'''
    
    def _generate_fastapi_model(self, model: Dict) -> str:
        """Generate SQLAlchemy model code"""
        fields_code = []
        for field in model['fields']:
            field_code = f"    {field['name']} = Column({self._python_type_to_sqlalchemy(field['type'])})"
            fields_code.append(field_code)
        
        return self.templates['fastapi']['model'].format(
            model_name=model['name'],
            table_name=model['name'].lower(),
            fields='\n'.join(fields_code)
        )
    
    def _path_to_function_name(self, path: str, method: str) -> str:
        """Convert API path to function name"""
        name = path.lstrip('/').replace('/', '_').replace('-', '_')
        return f"{method}_{name}" if name else method
    
    def _python_type_to_sqlalchemy(self, py_type: str) -> str:
        """Convert Python type to SQLAlchemy column type"""
        type_mapping = {
            'str': 'String',
            'int': 'Integer',
            'bool': 'Boolean',
            'datetime': 'DateTime',
            'float': 'Float'
        }
        return type_mapping.get(py_type, 'String')
    
    def _determine_middleware(self, analysis: Dict) -> List[str]:
        """Determine required middleware"""
        middleware = ['cors']
        
        if analysis.get('auth_requirements', {}).get('required'):
            middleware.append('authentication')
        
        return middleware
    
    def _determine_auth_method(self, analysis: Dict) -> str:
        """Determine authentication method"""
        auth_info = analysis.get('auth_requirements', {})
        
        if 'jwt' in auth_info.get('methods', []):
            return 'jwt'
        elif auth_info.get('required'):
            return 'session'
        else:
            return 'none'
    
    def _generate_dependencies(self, framework: str, database: str, middleware: List[str]) -> List[str]:
        """Generate package dependencies"""
        deps = []
        
        if framework == 'fastapi':
            deps.extend(['fastapi', 'uvicorn', 'python-multipart'])
            
            if database == 'postgresql':
                deps.extend(['sqlalchemy', 'psycopg2-binary'])
            elif database == 'sqlite':
                deps.extend(['sqlalchemy'])
            
            if 'authentication' in middleware:
                deps.extend(['python-jose[cryptography]', 'passlib[bcrypt]'])
        
        return deps
    
    def _infer_parameters(self, endpoint: Dict) -> List[Dict]:
        """Infer endpoint parameters"""
        return []
    
    def _infer_response_model(self, endpoint: Dict) -> str:
        """Infer response model for endpoint"""
        return "dict"
    
    def _infer_relationships(self, model_info: Dict) -> List[Dict]:
        """Infer model relationships"""
        return []

# Main integration class
class FullStackGenerator:
    """Main class that combines frontend analysis with backend generation"""
    
    def __init__(self):
        self.frontend_analyzer = FrontendAnalyzer()
        self.backend_generator = BackendCodeGenerator()
    
    def generate_from_frontend(self, frontend_code: str, preferences: Dict = None) -> Dict:
        """Generate complete backend from frontend code"""
        # Analyze frontend
        analysis = self.frontend_analyzer.analyze_code(frontend_code)
        
        # Generate backend specification
        backend_spec = self.backend_generator.generate_backend(analysis, preferences)
        
        # Generate code files
        code_files = self.backend_generator.generate_code_files(backend_spec)
        
        return {
            'frontend_analysis': analysis,
            'backend_spec': backend_spec,
            'code_files': code_files
        }
    
    def generate_from_url(self, url: str, preferences: Dict = None) -> Dict:
        """Generate backend from scraped frontend URL"""
        # This would integrate with the scraper to get frontend code
        # For now, return a placeholder
        return {
            'message': 'URL scraping integration coming soon',
            'url': url
        }
    
    def generate_from_figma(self, figma_url: str, preferences: Dict = None) -> Dict:
        """Generate backend from Figma design"""
        # This would integrate with Figma API
        return {
            'message': 'Figma integration coming soon',
            'figma_url': figma_url
        }

if __name__ == "__main__":
    # Example usage
    generator = FullStackGenerator()
    
    # Example frontend code
    frontend_code = """
    import React, { useState, useEffect } from 'react';
    import axios from 'axios';
    
    interface User {
        id: number;
        name: string;
        email: string;
    }
    
    function UserDashboard() {
        const [users, setUsers] = useState<User[]>([]);
        
        useEffect(() => {
            axios.get('/api/users').then(response => {
                setUsers(response.data);
            });
        }, []);
        
        const handleLogin = async (email: string, password: string) => {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                body: JSON.stringify({ email, password })
            });
        };
        
        return (
            <div>
                <h1>User Dashboard</h1>
                {users.map(user => (
                    <div key={user.id}>{user.name}</div>
                ))}
            </div>
        );
    }
    """
    
    result = generator.generate_from_frontend(frontend_code)
    print(json.dumps(result, indent=2, default=str))
