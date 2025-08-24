import os
import subprocess
import json
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import requests
from pathlib import Path
import tempfile
import shutil
import zipfile
from git import Repo
import docker
from kubernetes import client, config

@dataclass
class DeploymentConfig:
    platform: str
    environment: str
    domain: Optional[str] = None
    env_vars: Dict[str, str] = None
    database_url: Optional[str] = None

class AutomationEngine:
    """
    Comprehensive automation engine for deployment, GitHub integration, and CI/CD.
    """
    
    def __init__(self, api_keys: Dict[str, str]):
        self.api_keys = api_keys
        self.docker_client = None
        self.k8s_client = None
        self.setup_clients()
    
    def setup_clients(self):
        """Setup various API clients."""
        try:
            self.docker_client = docker.from_env()
        except:
            pass
        
        try:
            config.load_incluster_config()
            self.k8s_client = client.ApiClient()
        except:
            try:
                config.load_kube_config()
                self.k8s_client = client.ApiClient()
            except:
                pass
    
    async def deploy_to_vercel(self, project_path: str, project_name: str) -> Dict[str, Any]:
        """Deploy project to Vercel with full automation."""
        try:
            vercel_token = self.api_keys.get('vercel')
            if not vercel_token:
                raise ValueError("Vercel API token required")
            
            # Create deployment
            headers = {
                'Authorization': f'Bearer {vercel_token}',
                'Content-Type': 'application/json'
            }
            
            # Upload project files
            files_data = self._prepare_project_files(project_path)
            
            deployment_data = {
                'name': project_name,
                'files': files_data,
                'projectSettings': {
                    'framework': 'nextjs',
                    'buildCommand': 'npm run build',
                    'outputDirectory': '.next'
                }
            }
            
            response = requests.post(
                'https://api.vercel.com/v13/deployments',
                headers=headers,
                json=deployment_data
            )
            
            if response.status_code == 200:
                deployment = response.json()
                return {
                    'status': 'success',
                    'url': f"https://{deployment['url']}",
                    'deployment_id': deployment['id']
                }
            else:
                return {
                    'status': 'error',
                    'message': response.text
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def setup_supabase_project(self, project_name: str, database_schema: str) -> Dict[str, Any]:
        """Setup Supabase project with database schema."""
        try:
            supabase_url = self.api_keys.get('supabase_url')
            supabase_key = self.api_keys.get('supabase_key')
            
            if not supabase_url or not supabase_key:
                raise ValueError("Supabase credentials required")
            
            # Execute database schema
            headers = {
                'apikey': supabase_key,
                'Authorization': f'Bearer {supabase_key}',
                'Content-Type': 'application/json'
            }
            
            # Run SQL schema
            sql_response = requests.post(
                f'{supabase_url}/rest/v1/rpc/exec_sql',
                headers=headers,
                json={'sql': database_schema}
            )
            
            if sql_response.status_code == 200:
                return {
                    'status': 'success',
                    'database_url': supabase_url,
                    'message': 'Database schema applied successfully'
                }
            else:
                return {
                    'status': 'error',
                    'message': sql_response.text
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def create_github_repository(self, repo_name: str, project_path: str, private: bool = False) -> Dict[str, Any]:
        """Create GitHub repository and push code."""
        try:
            github_token = self.api_keys.get('github')
            if not github_token:
                raise ValueError("GitHub token required")
            
            # Create repository
            headers = {
                'Authorization': f'token {github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            repo_data = {
                'name': repo_name,
                'private': private,
                'auto_init': True,
                'description': f'AI-generated application: {repo_name}'
            }
            
            response = requests.post(
                'https://api.github.com/user/repos',
                headers=headers,
                json=repo_data
            )
            
            if response.status_code == 201:
                repo_info = response.json()
                
                # Initialize git and push code
                repo = Repo.init(project_path)
                origin = repo.create_remote('origin', repo_info['clone_url'])
                
                # Add all files
                repo.git.add(A=True)
                repo.index.commit('Initial commit - AI generated application')
                
                # Push to GitHub
                origin.push(refspec='main:main')
                
                return {
                    'status': 'success',
                    'repo_url': repo_info['html_url'],
                    'clone_url': repo_info['clone_url']
                }
            else:
                return {
                    'status': 'error',
                    'message': response.text
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _prepare_project_files(self, project_path: str) -> List[Dict[str, Any]]:
        """Prepare project files for deployment."""
        files_data = []
        
        for root, dirs, files in os.walk(project_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, project_path)
                
                # Skip certain files/directories
                if any(skip in relative_path for skip in ['.git', 'node_modules', '__pycache__', '.env']):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    files_data.append({
                        'file': relative_path,
                        'data': content
                    })
                except:
                    # Handle binary files
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    
                    files_data.append({
                        'file': relative_path,
                        'data': content.hex()
                    })
        
        return files_data
    
    async def setup_ci_cd_pipeline(self, repo_url: str, deployment_config: DeploymentConfig) -> Dict[str, Any]:
        """Setup CI/CD pipeline with GitHub Actions."""
        try:
            # Generate GitHub Actions workflow
            workflow_content = self._generate_github_workflow(deployment_config)
            
            # Create .github/workflows directory and workflow file
            workflow_path = '.github/workflows/deploy.yml'
            
            return {
                'status': 'success',
                'workflow_path': workflow_path,
                'workflow_content': workflow_content
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _generate_github_workflow(self, config: DeploymentConfig) -> str:
        """Generate GitHub Actions workflow for deployment."""
        workflow = f"""
name: Deploy to {config.platform}

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run tests
      run: npm test
    
    - name: Build application
      run: npm run build
    
    - name: Deploy to {config.platform}
      uses: vercel/action@v1
      with:
        vercel-token: ${{{{ secrets.VERCEL_TOKEN }}}}
        vercel-org-id: ${{{{ secrets.ORG_ID }}}}
        vercel-project-id: ${{{{ secrets.PROJECT_ID }}}}
"""
        
        return workflow
    
    async def monitor_deployment(self, deployment_id: str, platform: str) -> Dict[str, Any]:
        """Monitor deployment status and health."""
        try:
            if platform.lower() == 'vercel':
                return await self._monitor_vercel_deployment(deployment_id)
            else:
                return {
                    'status': 'unknown',
                    'message': f'Monitoring not implemented for {platform}'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def _monitor_vercel_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """Monitor Vercel deployment status."""
        try:
            vercel_token = self.api_keys.get('vercel')
            headers = {
                'Authorization': f'Bearer {vercel_token}'
            }
            
            response = requests.get(
                f'https://api.vercel.com/v13/deployments/{deployment_id}',
                headers=headers
            )
            
            if response.status_code == 200:
                deployment = response.json()
                return {
                    'status': deployment['readyState'],
                    'url': f"https://{deployment['url']}",
                    'created_at': deployment['createdAt']
                }
            else:
                return {
                    'status': 'error',
                    'message': response.text
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
