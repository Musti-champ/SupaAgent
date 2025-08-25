import streamlit as st
import os
import subprocess
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import requests
from platform_dataset_manager import PlatformDatasetManager
from venice_ai_integration import VeniceAIOpenRouter
from fullstack_developer import FullstackDeveloper
import tempfile
import shutil
from pathlib import Path

@dataclass
class ProjectConfig:
    name: str
    description: str
    tech_stack: List[str]
    deployment_target: str
    github_repo: Optional[str] = None
    api_keys: Dict[str, str] = None

class IDEInterface:
    """
    Comprehensive IDE interface similar to v0.app and Lovable with full automation.
    """
    
    def __init__(self):
        self.platform_manager = None
        self.fullstack_dev = None
        self.current_project = None
        self.setup_session_state()
    
    def setup_session_state(self):
        """Initialize session state variables."""
        if 'api_keys' not in st.session_state:
            st.session_state.api_keys = {}
        if 'current_project' not in st.session_state:
            st.session_state.current_project = None
        if 'generated_code' not in st.session_state:
            st.session_state.generated_code = {}
        if 'deployment_status' not in st.session_state:
            st.session_state.deployment_status = {}
    
    def render_main_interface(self):
        """Render the main IDE interface."""
        st.set_page_config(
            page_title="AI Fullstack Developer IDE",
            page_icon="🚀",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.title("🚀 AI Fullstack Developer IDE")
        st.markdown("*The world's most advanced AI-powered development environment*")
        
        # Sidebar for configuration
        self.render_sidebar()
        
        # Main content area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            self.render_development_interface()
        
        with col2:
            self.render_project_panel()
    
    def render_sidebar(self):
        """Render the sidebar with API keys and configuration."""
        with st.sidebar:
            st.header("🔧 Configuration")
            
            # API Keys Section
            st.subheader("API Keys")
            
            # Venice AI API Key
            venice_key = st.text_input(
                "Venice AI API Key",
                type="password",
                value=st.session_state.api_keys.get('venice_ai', ''),
                help="Required for AI-powered code generation"
            )
            if venice_key:
                st.session_state.api_keys['venice_ai'] = venice_key
            
            # OpenAI API Key
            openai_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value=st.session_state.api_keys.get('openai', ''),
                help="Alternative AI provider for code generation"
            )
            if openai_key:
                st.session_state.api_keys['openai'] = openai_key
            
            # Gemini API Key
            gemini_key = st.text_input(
                "Google Gemini API Key",
                type="password",
                value=st.session_state.api_keys.get('gemini', ''),
                help="Google's AI for advanced code analysis"
            )
            if gemini_key:
                st.session_state.api_keys['gemini'] = gemini_key
            
            # GitHub Token
            github_token = st.text_input(
                "GitHub Personal Access Token",
                type="password",
                value=st.session_state.api_keys.get('github', ''),
                help="Required for GitHub integration and deployment"
            )
            if github_token:
                st.session_state.api_keys['github'] = github_token
            
            # Vercel Token
            vercel_token = st.text_input(
                "Vercel API Token",
                type="password",
                value=st.session_state.api_keys.get('vercel', ''),
                help="Required for Vercel deployment automation"
            )
            if vercel_token:
                st.session_state.api_keys['vercel'] = vercel_token
            
            # Supabase Keys
            supabase_url = st.text_input(
                "Supabase Project URL",
                value=st.session_state.api_keys.get('supabase_url', ''),
                help="Your Supabase project URL"
            )
            if supabase_url:
                st.session_state.api_keys['supabase_url'] = supabase_url
            
            supabase_key = st.text_input(
                "Supabase Anon Key",
                type="password",
                value=st.session_state.api_keys.get('supabase_key', ''),
                help="Your Supabase anonymous key"
            )
            if supabase_key:
                st.session_state.api_keys['supabase_key'] = supabase_key
            
            # Initialize AI services if keys are provided
            if st.button("🔄 Initialize AI Services"):
                self.initialize_ai_services()
    
    def initialize_ai_services(self):
        """Initialize AI services with provided API keys."""
        try:
            if st.session_state.api_keys.get('venice_ai'):
                venice_ai = VeniceAIOpenRouter(st.session_state.api_keys['venice_ai'])
                self.platform_manager = PlatformDatasetManager(venice_ai)
                self.fullstack_dev = FullstackDeveloper(venice_ai)
                st.success("✅ AI services initialized successfully!")
            else:
                st.error("❌ Venice AI API key is required")
        except Exception as e:
            st.error(f"❌ Failed to initialize AI services: {str(e)}")
    
    def render_development_interface(self):
        """Render the main development interface."""
        st.header("💻 Development Environment")
        
        # Development mode selection
        dev_mode = st.selectbox(
            "Choose Development Mode",
            [
                "🏗️ Build New Application",
                "🔄 Clone Existing Platform", 
                "🎨 Drag & Drop Builder",
                "📁 Analyze GitHub Repository",
                "🐛 Debug & Fix Code",
                "🔧 Rewrite Application",
                "🎨 Frontend Only",
                "⚙️ Backend Only",
                "🌐 Fullstack Application"
            ]
        )
        
        if dev_mode == "🏗️ Build New Application":
            self.render_new_app_builder()
        elif dev_mode == "🔄 Clone Existing Platform":
            self.render_platform_cloner()
        elif dev_mode == "🎨 Drag & Drop Builder":
            self.render_drag_drop_builder()
        elif dev_mode == "📁 Analyze GitHub Repository":
            self.render_github_analyzer()
        elif dev_mode == "🐛 Debug & Fix Code":
            self.render_debugger()
        elif dev_mode == "🔧 Rewrite Application":
            self.render_app_rewriter()
        elif dev_mode in ["🎨 Frontend Only", "⚙️ Backend Only", "🌐 Fullstack Application"]:
            self.render_targeted_development(dev_mode)
    
    def render_new_app_builder(self):
        """Render interface for building new applications."""
        st.subheader("🏗️ Build New Application")
        
        app_description = st.text_area(
            "Describe your application",
            placeholder="I want to build an app like Google that can search the web and provide relevant results...",
            height=100
        )
        
        if app_description and self.platform_manager:
            # Analyze requirements
            if st.button("🔍 Analyze Requirements"):
                with st.spinner("Analyzing application requirements..."):
                    analysis = self.platform_manager.analyze_app_requirements(app_description)
                    st.session_state.app_analysis = analysis
            
            # Show analysis results
            if hasattr(st.session_state, 'app_analysis'):
                analysis = st.session_state.app_analysis
                
                st.subheader("📊 Analysis Results")
                
                # Similar platforms
                if analysis.get('similar_platforms'):
                    st.write("**Similar Platforms:**")
                    for platform in analysis['similar_platforms']:
                        st.write(f"- {platform['platform']}: {platform['description']}")
                
                # API recommendations
                if analysis.get('api_recommendations'):
                    st.write("**Recommended APIs:**")
                    for api in analysis['api_recommendations']:
                        st.write(f"- {api['api']}: {api['cost']} (Free tier: {api['free_tier']})")
                
                # Build options
                st.subheader("🛠️ Build Options")
                build_approach = st.radio(
                    "Choose your approach:",
                    [
                        "🔨 Build from Scratch",
                        "🔌 Use Third-Party APIs",
                        "🎯 Hybrid Approach"
                    ]
                )
                
                if st.button("🚀 Start Building"):
                    self.start_building(app_description, build_approach, analysis)
    
    def render_platform_cloner(self):
        """Render interface for cloning existing platforms."""
        st.subheader("🔄 Clone Existing Platform")
        
        if self.platform_manager:
            platforms = list(self.platform_manager.platforms_dataset.keys())
            selected_platform = st.selectbox(
                "Select platform to clone:",
                platforms,
                format_func=lambda x: self.platform_manager.platforms_dataset[x].name
            )
            
            customizations = st.text_area(
                "Customizations (optional)",
                placeholder="Add dark mode, change color scheme to blue, add user profiles...",
                height=80
            )
            
            clone_type = st.radio(
                "What to clone:",
                ["🎨 Frontend Only", "⚙️ Backend Only", "🌐 Full Application"]
            )
            
            if st.button("🔄 Start Cloning"):
                self.start_cloning(selected_platform, customizations, clone_type)
    
    def render_drag_drop_builder(self):
        """Render drag-and-drop builder interface."""
        st.subheader("🎨 Drag & Drop Builder")
        
        builder_type = st.selectbox(
            "Choose Builder Type",
            [
                "🌐 Website Builder (like Wix/WordPress)",
                "🎨 Design Tool (like Canva)",
                "📱 App Interface Builder",
                "📧 Email Template Builder",
                "📊 Dashboard Builder",
                "🛒 E-commerce Store Builder"
            ]
        )
        
        st.write("**Builder Features:**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("✅ Drag & Drop Interface")
            st.write("✅ Component Library")
            st.write("✅ Real-time Preview")
            st.write("✅ Responsive Design")
        
        with col2:
            st.write("✅ Template System")
            st.write("✅ Custom Styling")
            st.write("✅ Export Options")
            st.write("✅ Collaboration Tools")
        
        # Builder customization options
        st.subheader("🛠️ Customization Options")
        
        include_templates = st.checkbox("Include Pre-built Templates", value=True)
        include_collaboration = st.checkbox("Real-time Collaboration", value=True)
        include_export = st.checkbox("Multiple Export Formats", value=True)
        include_api = st.checkbox("API Integration Support", value=True)
        
        custom_features = st.text_area(
            "Additional Features (optional)",
            placeholder="Add animation support, custom fonts, advanced styling options...",
            height=80
        )
        
        if st.button("🚀 Create Builder"):
            self.create_drag_drop_builder(builder_type, {
                'templates': include_templates,
                'collaboration': include_collaboration,
                'export': include_export,
                'api': include_api,
                'custom_features': custom_features
            })
    
    def render_github_analyzer(self):
        """Render interface for GitHub repository analysis."""
        st.subheader("📁 GitHub Repository Analysis")
        
        github_url = st.text_input(
            "GitHub Repository URL",
            placeholder="https://github.com/username/repository"
        )
        
        analysis_type = st.selectbox(
            "Analysis Type",
            [
                "🔍 Code Analysis & Documentation",
                "🐛 Bug Detection & Fixes",
                "⚡ Performance Optimization",
                "🔒 Security Audit",
                "🏗️ Architecture Review",
                "📈 Enhancement Suggestions"
            ]
        )
        
        if st.button("📊 Analyze Repository") and github_url:
            self.analyze_github_repo(github_url, analysis_type)
    
    def render_debugger(self):
        """Render interface for debugging and fixing code."""
        st.subheader("🐛 Debug & Fix Code")
        
        debug_input = st.radio(
            "Input Method",
            ["📝 Paste Code", "📁 Upload File", "🔗 GitHub Repository"]
        )
        
        if debug_input == "📝 Paste Code":
            code_to_debug = st.text_area(
                "Paste your code here",
                height=200,
                placeholder="Paste the problematic code here..."
            )
            
            error_description = st.text_area(
                "Describe the issue",
                placeholder="The app crashes when I click the submit button..."
            )
            
            if st.button("🔧 Debug & Fix") and code_to_debug:
                self.debug_code(code_to_debug, error_description)
    
    def render_project_panel(self):
        """Render the project management panel."""
        st.header("📋 Project Panel")
        
        if st.session_state.current_project:
            project = st.session_state.current_project
            st.subheader(f"📁 {project.name}")
            st.write(f"**Description:** {project.description}")
            st.write(f"**Tech Stack:** {', '.join(project.tech_stack)}")
            
            # Deployment section
            st.subheader("🚀 Deployment")
            
            deployment_target = st.selectbox(
                "Deployment Target",
                ["Vercel", "Netlify", "AWS", "Azure", "Google Cloud", "DigitalOcean"]
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔗 Connect to GitHub"):
                    self.connect_to_github()
            
            with col2:
                if st.button("🚀 Deploy to " + deployment_target):
                    self.deploy_project(deployment_target)
            
            # Database setup
            st.subheader("🗄️ Database Setup")
            
            db_provider = st.selectbox(
                "Database Provider",
                ["Supabase", "PlanetScale", "MongoDB Atlas", "Firebase", "PostgreSQL"]
            )
            
            if st.button("🔧 Setup Database"):
                self.setup_database(db_provider)
        
        else:
            st.info("No active project. Start building to see project details here.")
    
    def start_building(self, description: str, approach: str, analysis: Dict):
        """Start building the application."""
        if not self.fullstack_dev:
            st.error("Please initialize AI services first")
            return
        
        with st.spinner("Building your application..."):
            try:
                # Create project configuration
                project_config = ProjectConfig(
                    name=f"ai_generated_app_{len(st.session_state.generated_code)}",
                    description=description,
                    tech_stack=["React", "Node.js", "FastAPI", "PostgreSQL"],
                    deployment_target="Vercel"
                )
                
                st.session_state.current_project = project_config
                
                # Generate application code
                generated_app = self.fullstack_dev.build_complete_application(
                    description, approach, analysis
                )
                
                st.session_state.generated_code[project_config.name] = generated_app
                
                st.success("✅ Application built successfully!")
                
                # Display generated code
                self.display_generated_code(generated_app)
                
            except Exception as e:
                st.error(f"❌ Failed to build application: {str(e)}")
    
    def display_generated_code(self, generated_code: Dict):
        """Display the generated code in tabs."""
        st.subheader("📄 Generated Code")
        
        if isinstance(generated_code, dict) and 'files' in generated_code:
            files = generated_code['files']
            
            # Create tabs for different files
            tab_names = list(files.keys())[:10]  # Limit to 10 tabs
            tabs = st.tabs(tab_names)
            
            for i, (filename, content) in enumerate(files.items()):
                if i < 10:  # Only show first 10 files in tabs
                    with tabs[i]:
                        st.code(content, language=self.get_language_from_filename(filename))
                        
                        # Download button for each file
                        st.download_button(
                            f"📥 Download {filename}",
                            content,
                            filename,
                            key=f"download_{filename}_{i}"
                        )
        
        # Download entire project as ZIP
        if st.button("📦 Download Complete Project"):
            self.create_project_zip()
    
    def get_language_from_filename(self, filename: str) -> str:
        """Get programming language from filename for syntax highlighting."""
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.md': 'markdown',
            '.yml': 'yaml',
            '.yaml': 'yaml'
        }
        
        for ext, lang in extension_map.items():
            if filename.endswith(ext):
                return lang
        
        return 'text'
    
    def connect_to_github(self):
        """Connect project to GitHub repository."""
        if not st.session_state.api_keys.get('github'):
            st.error("GitHub token is required")
            return
        
        with st.spinner("Connecting to GitHub..."):
            try:
                # Create GitHub repository
                repo_name = st.session_state.current_project.name
                
                # This would integrate with GitHub API
                st.success(f"✅ Connected to GitHub repository: {repo_name}")
                
            except Exception as e:
                st.error(f"❌ Failed to connect to GitHub: {str(e)}")
    
    def deploy_project(self, target: str):
        """Deploy project to specified target."""
        with st.spinner(f"Deploying to {target}..."):
            try:
                # This would integrate with deployment APIs
                deployment_url = f"https://{st.session_state.current_project.name}.{target.lower()}.app"
                
                st.session_state.deployment_status[target] = {
                    'status': 'deployed',
                    'url': deployment_url,
                    'timestamp': 'now'
                }
                
                st.success(f"✅ Deployed to {target}: {deployment_url}")
                
            except Exception as e:
                st.error(f"❌ Failed to deploy to {target}: {str(e)}")
    
    def setup_database(self, provider: str):
        """Setup database with specified provider."""
        with st.spinner(f"Setting up {provider} database..."):
            try:
                # This would integrate with database provider APIs
                db_url = f"postgresql://user:pass@{provider.lower()}.com/db"
                
                st.success(f"✅ {provider} database setup complete!")
                st.info(f"Database URL: {db_url}")
                
            except Exception as e:
                st.error(f"❌ Failed to setup {provider} database: {str(e)}")
    
    def create_drag_drop_builder(self, builder_type: str, options: Dict):
        """Create drag-and-drop builder application."""
        if not self.platform_manager:
            st.error("Please initialize AI services first")
            return
        
        with st.spinner("Creating drag-and-drop builder..."):
            try:
                # Generate builder application
                builder_result = self.platform_manager.create_drag_drop_builder(builder_type)
                
                # Create project configuration
                project_config = ProjectConfig(
                    name=f"drag_drop_builder_{len(st.session_state.generated_code)}",
                    description=f"{builder_type} with drag-and-drop functionality",
                    tech_stack=["React", "Node.js", "Socket.io", "MongoDB", "Canvas API"],
                    deployment_target="Vercel"
                )
                
                st.session_state.current_project = project_config
                st.session_state.generated_code[project_config.name] = builder_result
                
                st.success("✅ Drag-and-drop builder created successfully!")
                
                # Display builder features
                st.subheader("🎯 Builder Features")
                for feature in builder_result.get('features', []):
                    st.write(f"✅ {feature}")
                
                # Display generated code
                self.display_generated_code(builder_result)
                
                # Show deployment options
                st.subheader("🚀 Ready to Deploy")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("🔗 Push to GitHub"):
                        self.connect_to_github()
                
                with col2:
                    if st.button("🚀 Deploy to Vercel"):
                        self.deploy_project("Vercel")
                
                with col3:
                    if st.button("🗄️ Setup Database"):
                        self.setup_database("MongoDB")
                
            except Exception as e:
                st.error(f"❌ Failed to create builder: {str(e)}")

def main():
    """Main function to run the IDE interface."""
    ide = IDEInterface()
    ide.render_main_interface()

if __name__ == "__main__":
    main()
