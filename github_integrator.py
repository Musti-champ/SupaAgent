import requests
import json
import subprocess
import os
import tempfile
import shutil
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
from venice_ai_integration import VeniceAIOpenRouter

class GitHubIntegrator:
    """
    GitHub integration for cloning, analyzing, and enhancing repositories.
    """
    
    def __init__(self, venice_ai: VeniceAIOpenRouter, github_token: Optional[str] = None):
        self.venice_ai = venice_ai
        self.github_token = github_token
        self.logger = logging.getLogger(__name__)
        self.temp_dir = tempfile.mkdtemp()
        
        self.headers = {}
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"
    
    def clone_and_analyze_repo(self, repo_url: str) -> Dict[str, Any]:
        """
        Clone a GitHub repository and perform comprehensive analysis.
        """
        try:
            # Extract repo information
            repo_info = self._parse_github_url(repo_url)
            if not repo_info:
                return {"error": "Invalid GitHub URL"}
            
            # Get repository metadata from GitHub API
            api_data = self._get_repo_metadata(repo_info["owner"], repo_info["name"])
            
            # Clone repository
            clone_path = self._clone_repository(repo_url, repo_info["name"])
            
            # Analyze codebase
            code_analysis = self._analyze_repository_code(clone_path)
            
            # AI-powered analysis
            ai_insights = self._get_ai_insights(code_analysis, api_data)
            
            return {
                "repo_info": repo_info,
                "metadata": api_data,
                "code_analysis": code_analysis,
                "ai_insights": ai_insights,
                "clone_path": clone_path,
                "suggestions": self._generate_improvement_suggestions(code_analysis)
            }
            
        except Exception as e:
            self.logger.error(f"Repository analysis failed: {e}")
            return {"error": f"Analysis failed: {e}"}
    
    def enhance_repository(self, repo_analysis: Dict[str, Any], enhancement_type: str) -> Dict[str, str]:
        """
        Enhance a repository with new features, fixes, or improvements.
        """
        enhancement_prompts = {
            "add_tests": "Add comprehensive unit and integration tests",
            "improve_documentation": "Improve README and add comprehensive documentation",
            "add_ci_cd": "Add GitHub Actions CI/CD pipeline",
            "modernize_code": "Modernize code with latest best practices",
            "add_security": "Add security enhancements and vulnerability fixes",
            "performance_optimization": "Optimize code for better performance",
            "add_features": "Add new features based on repository analysis"
        }
        
        enhancement_description = enhancement_prompts.get(enhancement_type, enhancement_type)
        
        prompt = f"""
        Enhance this repository: {enhancement_description}
        
        Repository Analysis:
        {json.dumps(repo_analysis.get('code_analysis', {}), indent=2)[:4000]}
        
        AI Insights:
        {json.dumps(repo_analysis.get('ai_insights', {}), indent=2)[:2000]}
        
        Generate:
        1. Enhanced/new code files
        2. Updated configuration files
        3. Documentation updates
        4. Setup/deployment instructions
        
        Focus on:
        - Production-ready code
        - Best practices implementation
        - Comprehensive error handling
        - Security considerations
        - Performance optimization
        
        Return as structured code blocks with file names.
        """
        
        enhanced_code = self._generate_code_with_ai(prompt)
        return self._parse_generated_code(enhanced_code)
    
    def debug_repository_issues(self, repo_analysis: Dict[str, Any], issue_description: str = "") -> Dict[str, Any]:
        """
        Debug and fix issues in a repository.
        """
        prompt = f"""
        Debug and fix issues in this repository:
        
        Issue Description: {issue_description}
        
        Repository Analysis:
        {json.dumps(repo_analysis.get('code_analysis', {}), indent=2)[:4000]}
        
        Provide:
        1. Issue identification and root cause analysis
        2. Fixed code with explanations
        3. Prevention strategies
        4. Testing recommendations
        5. Monitoring suggestions
        
        Focus on:
        - Security vulnerabilities
        - Performance bottlenecks
        - Code quality issues
        - Dependency problems
        - Configuration errors
        
        Return detailed analysis and fixes.
        """
        
        debug_result = self._generate_code_with_ai(prompt)
        
        return {
            "debug_analysis": debug_result,
            "fixed_files": self._parse_generated_code(debug_result),
            "recommendations": self._extract_recommendations(debug_result)
        }
    
    def rewrite_repository(self, repo_analysis: Dict[str, Any], target_stack: str, requirements: str = "") -> Dict[str, str]:
        """
        Completely rewrite a repository with a new tech stack.
        """
        prompt = f"""
        Completely rewrite this repository using {target_stack}:
        
        Original Repository Analysis:
        {json.dumps(repo_analysis.get('code_analysis', {}), indent=2)[:4000]}
        
        Requirements: {requirements}
        
        Generate a complete rewrite with:
        1. Modern architecture and patterns
        2. Latest best practices
        3. Comprehensive error handling
        4. Security implementations
        5. Performance optimizations
        6. Testing setup
        7. Documentation
        8. Deployment configuration
        
        Target Stack: {target_stack}
        
        Return as structured code blocks with complete file structure.
        """
        
        rewritten_code = self._generate_code_with_ai(prompt)
        return self._parse_generated_code(rewritten_code)
    
    def _parse_github_url(self, url: str) -> Optional[Dict[str, str]]:
        """Parse GitHub URL to extract owner and repository name."""
        try:
            # Handle different GitHub URL formats
            if url.startswith('https://github.com/'):
                parts = url.replace('https://github.com/', '').split('/')
                return {"owner": parts[0], "name": parts[1].replace('.git', '')}
            return None
        except IndexError:
            return None
    
    def _get_repo_metadata(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository metadata from GitHub API."""
        try:
            response = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"GitHub API error: {e}")
            return {}
    
    def _clone_repository(self, repo_url: str, repo_name: str) -> str:
        """Clone repository to temporary directory."""
        clone_path = os.path.join(self.temp_dir, repo_name)
        subprocess.run(['git', 'clone', repo_url, clone_path], check=True, capture_output=True)
        return clone_path
    
    def _analyze_repository_code(self, repo_path: str) -> Dict[str, Any]:
        """Analyze repository code structure and content."""
        analysis = {
            "file_structure": {},
            "languages": {},
            "frameworks": [],
            "dependencies": {},
            "config_files": [],
            "documentation": [],
            "tests": [],
            "security_files": [],
            "ci_cd_files": []
        }
        
        # Walk through repository
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]
            
            for file in files:
                if file.startswith('.'):
                    continue
                
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_path)
                ext = os.path.splitext(file)[1].lower()
                
                # Count file types
                if ext:
                    analysis["languages"][ext] = analysis["languages"].get(ext, 0) + 1
                
                # Identify special files
                special_files = {
                    'package.json': 'dependencies',
                    'requirements.txt': 'dependencies',
                    'Cargo.toml': 'dependencies',
                    'go.mod': 'dependencies',
                    'pom.xml': 'dependencies',
                    'Dockerfile': 'config_files',
                    'docker-compose.yml': 'config_files',
                    '.github/workflows': 'ci_cd_files',
                    'README.md': 'documentation',
                    'test': 'tests',
                    'spec': 'tests',
                    'security.md': 'security_files'
                }
                
                for pattern, category in special_files.items():
                    if pattern in file.lower() or pattern in rel_path.lower():
                        analysis[category].append(rel_path)
                
                # Read key files for framework detection
                if file == 'package.json':
                    try:
                        with open(file_path, 'r') as f:
                            package_data = json.load(f)
                            analysis["dependencies"]["npm"] = {
                                **package_data.get('dependencies', {}),
                                **package_data.get('devDependencies', {})
                            }
                            
                            # Detect frameworks
                            deps = analysis["dependencies"]["npm"]
                            frameworks = {
                                'react': 'React',
                                'vue': 'Vue.js',
                                '@angular/core': 'Angular',
                                'express': 'Express.js',
                                'fastapi': 'FastAPI',
                                'django': 'Django',
                                'flask': 'Flask'
                            }
                            
                            for dep, framework in frameworks.items():
                                if dep in deps:
                                    analysis["frameworks"].append(framework)
                    except:
                        pass
        
        return analysis
    
    def _get_ai_insights(self, code_analysis: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI-powered insights about the repository."""
        prompt = f"""
        Analyze this repository and provide insights:
        
        Code Analysis:
        {json.dumps(code_analysis, indent=2)[:3000]}
        
        Repository Metadata:
        {json.dumps(metadata, indent=2)[:1000]}
        
        Provide insights on:
        1. Architecture and design patterns
        2. Code quality assessment
        3. Security considerations
        4. Performance potential
        5. Maintainability score
        6. Suggested improvements
        7. Technology stack assessment
        
        Return as structured JSON.
        """
        
        return self.venice_ai.analyze_content(prompt, "repository_insights")
    
    def _generate_improvement_suggestions(self, code_analysis: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions based on code analysis."""
        suggestions = []
        
        # Check for missing tests
        if not code_analysis.get("tests"):
            suggestions.append("Add comprehensive test suite")
        
        # Check for missing CI/CD
        if not code_analysis.get("ci_cd_files"):
            suggestions.append("Add CI/CD pipeline with GitHub Actions")
        
        # Check for missing documentation
        if not code_analysis.get("documentation"):
            suggestions.append("Add comprehensive documentation and README")
        
        # Check for security files
        if not code_analysis.get("security_files"):
            suggestions.append("Add security policy and vulnerability reporting")
        
        # Check for modern practices
        languages = code_analysis.get("languages", {})
        if ".js" in languages and ".ts" not in languages:
            suggestions.append("Consider migrating to TypeScript for better type safety")
        
        return suggestions
    
    def _generate_code_with_ai(self, prompt: str) -> str:
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
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Code generation error: {e}")
            return f"Error generating code: {e}"
    
    def _parse_generated_code(self, code: str) -> Dict[str, str]:
        """Parse generated code into separate files."""
        files = {}
        current_file = None
        current_content = []
        
        lines = code.split('\n')
        for line in lines:
            if line.startswith('```') and ('file=' in line or any(ext in line for ext in ['.js', '.jsx', '.ts', '.tsx', '.py', '.css', '.json', '.yml', '.yaml', '.md'])):
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
    
    def _extract_recommendations(self, debug_result: str) -> List[str]:
        """Extract recommendations from debug result."""
        # Simple extraction - in practice, this could be more sophisticated
        recommendations = []
        lines = debug_result.split('\n')
        
        for line in lines:
            if 'recommend' in line.lower() or 'suggest' in line.lower():
                recommendations.append(line.strip())
        
        return recommendations[:10]  # Limit to 10 recommendations
    
    def cleanup(self):
        """Clean up temporary files."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
