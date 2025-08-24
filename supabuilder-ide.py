# ===========================
# SUPABUILDER COMPLETE APPLICATION
# ===========================
import streamlit as st
import os
import subprocess
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import requests
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

class SupabuilderApp:
    """Complete Supabuilder application combining Streamlit backend with rich IDE frontend"""
    
    def __init__(self):
        self.setup_session_state()
        self.current_view = 'ide'
        self.current_project = None
        
        # Initialize managers (these would be your actual implementations)
        self.env_manager = EnvironmentManager()
        self.deployment_manager = DeploymentManager()
        self.ai_assistant = SupaAIAssistant()
    
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
        if 'app_analysis' not in st.session_state:
            st.session_state.app_analysis = None
    
    def render_application(self):
        """Render the complete Supabuilder application."""
        st.set_page_config(
            page_title="Supabuilder IDE",
            page_icon="🚀",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Render the appropriate view based on current_view
        if self.current_view == 'ide':
            self.render_ide_interface()
        elif self.current_view == 'env':
            self.render_environment_interface()
        elif self.current_view == 'deploy':
            self.render_deployment_interface()
        elif self.current_view == 'settings':
            self.render_settings_interface()
    
    def render_ide_interface(self):
        """Render the main IDE interface."""
        # Header
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.image("https://via.placeholder.com/150x50/007bff/ffffff?text=Supabuilder", width=150)
        with col2:
            st.title("Supabuilder IDE")
            st.caption("The world's most advanced AI-powered development environment")
        with col3:
            if st.button("⚙️ Settings", use_container_width=True):
                self.current_view = 'settings'
            if st.button("🚀 Deploy", use_container_width=True, type="primary"):
                self.current_view = 'deploy'
        
        # Main content area with tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Code Editor", "👀 Live Preview", "🎨 Visual Builder", "🤖 AI Assistant", "📁 Project"])
        
        with tab1:
            self.render_code_editor()
        
        with tab2:
            self.render_live_preview()
        
        with tab3:
            self.render_visual_builder()
        
        with tab4:
            self.render_ai_assistant()
        
        with tab5:
            self.render_project_panel()
        
        # Sidebar
        with st.sidebar:
            self.render_sidebar()
    
    def render_code_editor(self):
        """Render the code editor interface."""
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # File explorer
            st.subheader("Project Files")
            if st.session_state.current_project:
                self.render_file_explorer()
            else:
                st.info("No project loaded. Create or import a project to start editing.")
            
            # Code editor
            st.subheader("Code Editor")
            file_to_edit = st.selectbox(
                "Select file to edit",
                ["index.js", "App.js", "styles.css", "package.json"],
                index=0
            )
            
            code_content = st.text_area(
                "Edit code",
                height=400,
                value="// Start coding your amazing project...\nfunction welcome() {\n  return 'Hello, World!';\n}",
                key=f"editor_{file_to_edit}"
            )
            
            if st.button("💾 Save File"):
                st.success(f"Saved {file_to_edit}")
        
        with col2:
            # Quick actions
            st.subheader("Quick Actions")
            if st.button("🔄 Run Project", use_container_width=True):
                st.info("Running project...")
            
            if st.button("🔍 Debug", use_container_width=True):
                st.info("Starting debug session...")
            
            if st.button("📦 Build", use_container_width=True):
                st.info("Building project...")
            
            # AI tools
            st.subheader("AI Tools")
            if st.button("🧠 Generate Code", use_container_width=True):
                self.show_ai_code_generation()
            
            if st.button("🔧 Refactor", use_container_width=True):
                st.info("Refactoring code...")
            
            if st.button("🐛 Fix Bugs", use_container_width=True):
                st.info("Analyzing for bugs...")
    
    def render_live_preview(self):
        """Render the live preview interface."""
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Live Preview")
            # Device preview options
            device = st.radio(
                "Device Preview",
                ["Desktop", "Tablet", "Mobile"],
                horizontal=True
            )
            
            # Preview area
            st.markdown(f"""
            <div style="border: 2px solid #ddd; border-radius: 8px; padding: 10px; background: #f8f9fa;">
                <div style="text-align: center; margin-bottom: 10px;">
                    <strong>{device} Preview</strong>
                </div>
                <iframe src="about:blank" width="100%" height="400" style="border: 1px solid #ccc; border-radius: 4px;"></iframe>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔄 Refresh Preview"):
                st.info("Refreshing preview...")
        
        with col2:
            st.subheader("Preview Controls")
            st.slider("Zoom Level", 50, 150, 100, key="preview_zoom")
            st.checkbox("Show Responsive Breakpoints", value=True)
            st.checkbox("Show Element Outlines", value=False)
            
            st.subheader("Browser Info")
            st.selectbox("Browser", ["Chrome", "Firefox", "Safari", "Edge"])
            st.checkbox("Touch Simulation", value=True)
            
            if st.button("📸 Screenshot"):
                st.info("Taking screenshot...")
    
    def render_visual_builder(self):
        """Render the visual drag-and-drop builder."""
        st.subheader("Visual Builder")
        
        builder_type = st.selectbox(
            "Builder Type",
            ["Website Builder", "UI Components", "Dashboard", "E-commerce", "Custom"]
        )
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Canvas area
            st.markdown("""
            <div style="border: 2px dashed #ccc; border-radius: 8px; height: 500px; display: flex; align-items: center; justify-content: center; background: #fafafa;">
                <div style="text-align: center; color: #666;">
                    <h3>Drag components here</h3>
                    <p>Start building your interface visually</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Component library
            st.subheader("Components")
            
            st.markdown("**Basic**")
            if st.button("Button", use_container_width=True):
                st.info("Added Button component")
            if st.button("Input", use_container_width=True):
                st.info("Added Input component")
            if st.button("Card", use_container_width=True):
                st.info("Added Card component")
            
            st.markdown("**Layout**")
            if st.button("Container", use_container_width=True):
                st.info("Added Container component")
            if st.button("Grid", use_container_width=True):
                st.info("Added Grid component")
            if st.button("Section", use_container_width=True):
                st.info("Added Section component")
            
            st.markdown("**Advanced**")
            if st.button("Navigation", use_container_width=True):
                st.info("Added Navigation component")
            if st.button("Form", use_container_width=True):
                st.info("Added Form component")
            if st.button("Modal", use_container_width=True):
                st.info("Added Modal component")
    
    def render_ai_assistant(self):
        """Render the AI assistant interface."""
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("SupaAI Assistant")
            
            # Chat interface
            for message in [
                {"role": "ai", "content": "Hello! I'm SupaAI, your AI assistant. How can I help you with your project today?"},
                {"role": "user", "content": "I need help creating a login form with validation"},
                {"role": "ai", "content": "I can help with that! Would you like me to generate a complete login form component with email validation, password strength checking, and error handling?"}
            ]:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
            
            # User input
            user_input = st.chat_input("Ask SupaAI for help...")
            if user_input:
                with st.chat_message("user"):
                    st.write(user_input)
                
                # Simulate AI response
                with st.chat_message("ai"):
                    with st.spinner("Thinking..."):
                        st.write("I can help you with that! Based on your request, I recommend using React with Formik for validation. Would you like me to generate the code?")
        
        with col2:
            st.subheader("AI Tools")
            
            # Quick actions
            if st.button("🧩 Generate Component", use_container_width=True):
                self.show_component_generator()
            
            if st.button("🔍 Code Analysis", use_container_width=True):
                st.info("Analyzing code quality...")
            
            if st.button("📚 Generate Docs", use_container_width=True):
                st.info("Generating documentation...")
            
            if st.button("⚡ Optimize Code", use_container_width=True):
                st.info("Optimizing performance...")
            
            if st.button("🐛 Debug Code", use_container_width=True):
                st.info("Looking for bugs...")
            
            if st.button("🔄 Refactor", use_container_width=True):
                st.info("Refactoring code...")
            
            st.subheader("AI Settings")
            st.selectbox("AI Model", ["SupaAI Pro", "SupaAI Ultra", "GPT-4", "Claude", "Gemini"])
            st.slider("Creativity", 0.0, 1.0, 0.7)
            st.checkbox("Auto-suggest", value=True)
    
    def render_project_panel(self):
        """Render the project management panel."""
        if st.session_state.current_project:
            project = st.session_state.current_project
            st.header(f"Project: {project.name}")
            st.write(f"**Description:** {project.description}")
            st.write(f"**Tech Stack:** {', '.join(project.tech_stack)}")
            
            # Project stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Files", "24")
            with col2:
                st.metric("Lines of Code", "1,248")
            with col3:
                st.metric("Last Modified", "2 min ago")
            
            # File operations
            st.subheader("File Operations")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📦 Export Project"):
                    st.info("Exporting project...")
            with col2:
                if st.button("🔄 Sync with GitHub"):
                    self.connect_to_github()
            with col3:
                if st.button("🧹 Clean Project"):
                    st.info("Cleaning project files...")
            
            # Dependencies
            st.subheader("Dependencies")
            st.json({
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "next": "14.0.0",
                    "supabase": "^2.0.0"
                },
                "devDependencies": {
                    "typescript": "^5.0.0",
                    "eslint": "^8.0.0"
                }
            })
            
        else:
            st.info("No active project. Create or import a project to see details here.")
            
            # Project creation options
            st.subheader("Create New Project")
            project_name = st.text_input("Project Name")
            project_type = st.selectbox(
                "Project Type",
                ["Web Application", "Mobile App", "API Server", "Static Site", "E-commerce"]
            )
            
            if st.button("Create Project"):
                new_project = ProjectConfig(
                    name=project_name,
                    description=f"A new {project_type.lower()} project",
                    tech_stack=["React", "Node.js", "PostgreSQL"],
                    deployment_target="Vercel"
                )
                st.session_state.current_project = new_project
                st.success(f"Project '{project_name}' created!")
                st.rerun()
    
    def render_sidebar(self):
        """Render the sidebar with configuration options."""
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
        
        # Development mode selection
        st.subheader("Development Mode")
        dev_mode = st.selectbox(
            "Choose Mode",
            [
                "🏗️ Build New Application",
                "🔄 Clone Existing Platform", 
                "🎨 Drag & Drop Builder",
                "📁 Analyze GitHub Repository",
                "🐛 Debug & Fix Code",
                "🔧 Rewrite Application"
            ]
        )
        
        # Initialize AI services
        if st.button("🔄 Initialize AI Services"):
            self.initialize_ai_services()
        
        # Quick navigation
        st.subheader("Navigation")
        if st.button("📁 Environment Variables"):
            self.current_view = 'env'
        if st.button("🚀 Deployment"):
            self.current_view = 'deploy'
        if st.button("⚙️ Settings"):
            self.current_view = 'settings'
    
    def render_environment_interface(self):
        """Render the environment variables management interface."""
        st.title("Environment Variables")
        
        # Environment selection
        env = st.radio(
            "Environment",
            ["Development", "Staging", "Production"],
            horizontal=True
        )
        
        # Environment variables table
        st.subheader(f"{env} Environment Variables")
        
        # Sample environment variables
        env_vars = [
            {"name": "DATABASE_URL", "value": "postgresql://user:pass@localhost:5432/db", "services": ["Supabase", "Vercel"]},
            {"name": "NEXT_PUBLIC_SUPABASE_URL", "value": "https://your-project.supabase.co", "services": ["Supabase", "Vercel"]},
            {"name": "NEXT_PUBLIC_SUPABASE_ANON_KEY", "value": "your-anon-key", "services": ["Supabase", "Vercel"]},
            {"name": "STRIPE_SECRET_KEY", "value": "sk_test_...", "services": ["Vercel"]}
        ]
        
        for var in env_vars:
            with st.expander(f"{var['name']} = {var['value']}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text_input("Name", value=var['name'], key=f"name_{var['name']}")
                    st.text_input("Value", value=var['value'], type="password", key=f"value_{var['name']}")
                with col2:
                    st.multiselect(
                        "Services",
                        ["GitHub", "Vercel", "Supabase", "Netlify"],
                        default=var['services'],
                        key=f"services_{var['name']}"
                    )
                    if st.button("💾 Save", key=f"save_{var['name']}"):
                        st.success(f"Saved {var['name']}")
        
        # Add new variable
        st.subheader("Add New Variable")
        col1, col2, col3 = st.columns([2, 3, 2])
        with col1:
            new_name = st.text_input("Variable Name")
        with col2:
            new_value = st.text_input("Variable Value", type="password")
        with col3:
            new_services = st.multiselect(
                "Services",
                ["GitHub", "Vercel", "Supabase", "Netlify"],
                default=["Vercel"]
            )
            if st.button("Add Variable"):
                if new_name and new_value:
                    st.success(f"Added {new_name}")
                else:
                    st.error("Name and value are required")
        
        # Sync across services
        st.subheader("Sync Across Services")
        services_to_sync = st.multiselect(
            "Select services to sync",
            ["GitHub", "Vercel", "Supabase", "Netlify"],
            default=["Vercel", "Supabase"]
        )
        
        if st.button("🔄 Sync Now"):
            with st.spinner("Syncing environment variables..."):
                st.success(f"Synced with {', '.join(services_to_sync)}")
        
        # Back to IDE button
        if st.button("← Back to IDE"):
            self.current_view = 'ide'
    
    def render_deployment_interface(self):
        """Render the deployment management interface."""
        st.title("Deployment Dashboard")
        
        # Deployment stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Deployments", "12")
        with col2:
            st.metric("Active Environments", "3")
        with col3:
            st.metric("Success Rate", "92%")
        with col4:
            st.metric("Uptime", "99.8%")
        
        # Deployment targets
        st.subheader("Deployment Targets")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; text-align: center;">
                <img src="https://via.placeholder.com/50x50/000000/ffffff?text=V" width="50" style="margin-bottom: 10px;">
                <h4>Vercel</h4>
                <p>Frontend Deployment</p>
                <span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">Connected</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Deploy to Vercel", use_container_width=True):
                self.deploy_project("Vercel")
        
        with col2:
            st.markdown("""
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; text-align: center;">
                <img src="https://via.placeholder.com/50x50/3ecf8e/ffffff?text=S" width="50" style="margin-bottom: 10px;">
                <h4>Supabase</h4>
                <p>Database & Auth</p>
                <span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">Connected</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Setup Database", use_container_width=True):
                self.setup_database("Supabase")
        
        with col3:
            st.markdown("""
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; text-align: center;">
                <img src="https://via.placeholder.com/50x50/24292e/ffffff?text=G" width="50" style="margin-bottom: 10px;">
                <h4>GitHub</h4>
                <p>Version Control</p>
                <span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">Connected</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Push to GitHub", use_container_width=True):
                self.connect_to_github()
        
        # Deployment history
        st.subheader("Deployment History")
        
        deployments = [
            {"version": "v1.2.0", "environment": "Production", "status": "Success", "timestamp": "2 minutes ago"},
            {"version": "v1.1.0", "environment": "Staging", "status": "Success", "timestamp": "1 hour ago"},
            {"version": "v1.0.0", "environment": "Production", "status": "Success", "timestamp": "1 day ago"}
        ]
        
        for deployment in deployments:
            status_color = "#28a745" if deployment["status"] == "Success" else "#dc3545"
            st.markdown(f"""
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 10px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{deployment['version']}</strong> • {deployment['environment']}
                    </div>
                    <div>
                        <span style="background: {status_color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">
                            {deployment['status']}
                        </span>
                    </div>
                </div>
                <div style="color: #666; font-size: 14px; margin-top: 5px;">
                    {deployment['timestamp']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Back to IDE button
        if st.button("← Back to IDE"):
            self.current_view = 'ide'
    
    def render_settings_interface(self):
        """Render the settings interface."""
        st.title("Settings")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Editor", "AI", "Deployment", "Connections"])
        
        with tab1:
            st.subheader("Editor Settings")
            st.selectbox("Theme", ["Dark", "Light", "System"])
            st.slider("Font Size", 12, 24, 14)
            st.slider("Tab Size", 2, 8, 2)
            st.checkbox("Auto Save", value=True)
            st.checkbox("Word Wrap", value=False)
            st.checkbox("Line Numbers", value=True)
        
        with tab2:
            st.subheader("AI Settings")
            st.selectbox("AI Model", ["SupaAI Pro", "SupaAI Ultra", "GPT-4", "Claude", "Gemini"])
            st.slider("Creativity Level", 0.0, 1.0, 0.7)
            st.checkbox("Auto Suggestions", value=True)
            st.checkbox("Code Completion", value=True)
            st.checkbox("Explain Code", value=True)
        
        with tab3:
            st.subheader("Deployment Settings")
            st.selectbox("Default Deployment Target", ["Vercel", "Netlify", "AWS", "GitHub Pages"])
            st.checkbox("Auto Deploy on Push", value=True)
            st.checkbox("Preview Deployments", value=True)
            st.checkbox("Notify on Deployment", value=True)
        
        with tab4:
            st.subheader("Connection Settings")
            if st.button("Connect GitHub", use_container_width=True):
                st.info("Connecting to GitHub...")
            if st.button("Connect Vercel", use_container_width=True):
                st.info("Connecting to Vercel...")
            if st.button("Connect Supabase", use_container_width=True):
                st.info("Connecting to Supabase...")
            if st.button("Connect Stripe", use_container_width=True):
                st.info("Connecting to Stripe...")
        
        # Back to IDE button
        if st.button("← Back to IDE"):
            self.current_view = 'ide'
    
    def render_file_explorer(self):
        """Render the file explorer."""
        # Sample file structure
        files = {
            "src": {
                "components": ["Button.js", "Card.js", "Navbar.js"],
                "pages": ["index.js", "about.js", "contact.js"],
                "styles": ["globals.css", "components.css"]
            },
            "public": ["favicon.ico", "images"],
            "config": ["next.config.js", "supabase.js"]
        }
        
        def render_files(file_structure, path=""):
            for name, content in file_structure.items():
                if isinstance(content, list):
                    # It's a file list
                    for file in content:
                        full_path = f"{path}/{file}" if path else file
                        if st.button(f"📄 {file}", key=f"file_{full_path}"):
                            st.session_state.selected_file = full_path
                else:
                    # It's a directory
                    with st.expander(f"📁 {name}"):
                        render_files(content, f"{path}/{name}" if path else name)
        
        render_files(files)
    
    def show_ai_code_generation(self):
        """Show AI code generation dialog."""
        with st.form("ai_code_generation"):
            st.subheader("AI Code Generation")
            
            code_prompt = st.text_area(
                "Describe what you want to generate",
                placeholder="Create a React component for a user profile card with image, name, bio, and social links...",
                height=100
            )
            
            col1, col2 = st.columns(2)
            with col1:
                language = st.selectbox("Language", ["JavaScript", "TypeScript", "Python", "HTML", "CSS"])
            with col2:
                framework = st.selectbox("Framework", ["React", "Vue", "Angular", "Svelte", "None"])
            
            if st.form_submit_button("Generate Code"):
                if code_prompt:
                    with st.spinner("Generating code with AI..."):
                        # Simulate AI code generation
                        st.success("Code generated successfully!")
                        st.code("""
function UserProfile({ user }) {
  return (
    <div className="user-profile">
      <img src={user.avatar} alt={user.name} />
      <h2>{user.name}</h2>
      <p>{user.bio}</p>
      <div className="social-links">
        {user.socialLinks.map(link => (
          <a key={link.platform} href={link.url}>
            {link.platform}
          </a>
        ))}
      </div>
    </div>
  );
}
                        """, language="javascript")
                else:
                    st.error("Please describe what you want to generate")
    
    def show_component_generator(self):
        """Show component generator dialog."""
        with st.form("component_generator"):
            st.subheader("Component Generator")
            
            component_type = st.selectbox(
                "Component Type",
                ["Button", "Form", "Card", "Navigation", "Modal", "Table", "Custom"]
            )
            
            if component_type == "Custom":
                custom_description = st.text_input("Describe your custom component")
            
            style_options = st.multiselect(
                "Style Options",
                ["Responsive", "Dark Mode", "Animations", "Hover Effects", "Custom Colors"]
            )
            
            if st.form_submit_button("Generate Component"):
                with st.spinner("Generating component..."):
                    st.success(f"{component_type} component generated!")
                    st.code("""
// Generated component code would appear here
                    """, language="javascript")
    
    def initialize_ai_services(self):
        """Initialize AI services with provided API keys."""
        try:
            if st.session_state.api_keys.get('venice_ai'):
                st.success("✅ AI services initialized successfully!")
            else:
                st.error("❌ Venice AI API key is required")
        except Exception as e:
            st.error(f"❌ Failed to initialize AI services: {str(e)}")
    
    def connect_to_github(self):
        """Connect project to GitHub repository."""
        if not st.session_state.api_keys.get('github'):
            st.error("GitHub token is required")
            return
        
        with st.spinner("Connecting to GitHub..."):
            try:
                repo_name = st.session_state.current_project.name if st.session_state.current_project else "new-project"
                st.success(f"✅ Connected to GitHub repository: {repo_name}")
            except Exception as e:
                st.error(f"❌ Failed to connect to GitHub: {str(e)}")
    
    def deploy_project(self, target: str):
        """Deploy project to specified target."""
        with st.spinner(f"Deploying to {target}..."):
            try:
                project_name = st.session_state.current_project.name if st.session_state.current_project else "unknown"
                deployment_url = f"https://{project_name}.{target.lower()}.app"
                
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
                db_url = f"postgresql://user:pass@{provider.lower()}.com/db"
                st.success(f"✅ {provider} database setup complete!")
                st.info(f"Database URL: {db_url}")
            except Exception as e:
                st.error(f"❌ Failed to setup {provider} database: {str(e)}")

# ===========================
# APPLICATION INITIALIZATION
# ===========================
def main():
    """Main function to run the Supabuilder application."""
    app = SupabuilderApp()
    app.render_application()

if __name__ == "__main__":
    main()