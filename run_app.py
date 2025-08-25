#!/usr/bin/env python3
"""
AI Fullstack Developer - Main Application Runner
Launches the comprehensive AI development environment.
"""

import os
import sys
import json
from pathlib import Path

def check_setup():
    """Check if the system is properly configured"""
    config_file = "config.json"
    env_file = ".env"
    
    if not os.path.exists(config_file) or not os.path.exists(env_file):
        print("❌ System not configured. Please run setup first:")
        print("python install_and_setup.py")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        if not config.get('api_keys', {}).get('VENICE_AI_API_KEY'):
            print("⚠️  Venice AI API key not found. Some features may be limited.")
        
        return True
    except Exception as e:
        print(f"❌ Error reading configuration: {e}")
        return False

def main():
    """Main application entry point"""
    print("🎯 AI Fullstack Developer")
    print("=" * 40)
    
    if not check_setup():
        return
    
    print("🚀 Starting AI Fullstack Developer...")
    print("\nAvailable modes:")
    print("1. IDE Interface (Recommended)")
    print("2. Command Line Interface")
    print("3. Platform Dataset Manager")
    print("4. Drag & Drop Builder")
    
    choice = input("\nSelect mode (1-4): ").strip()
    
    try:
        if choice == "1":
            from ide_interface import AIFullstackIDE
            ide = AIFullstackIDE()
            ide.run()
        elif choice == "2":
            from fullstack_developer import FullstackDeveloper
            developer = FullstackDeveloper()
            developer.interactive_mode()
        elif choice == "3":
            from platform_dataset_manager import PlatformDatasetManager
            manager = PlatformDatasetManager()
            manager.interactive_study()
        elif choice == "4":
            from drag_drop_builder_engine import DragDropBuilderEngine
            builder = DragDropBuilderEngine()
            builder.launch_builder()
        else:
            print("Invalid choice. Starting IDE interface...")
            from ide_interface import AIFullstackIDE
            ide = AIFullstackIDE()
            ide.run()
    except ImportError as e:
        print(f"❌ Error importing modules: {e}")
        print("Please ensure all dependencies are installed:")
        print("python install_and_setup.py")
    except Exception as e:
        print(f"❌ Error starting application: {e}")

if __name__ == "__main__":
    main()
