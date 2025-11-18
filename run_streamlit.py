"""
Streamlit launcher script for Vietnamese Traffic Law QA System.
This script sets up the correct Python path and runs Streamlit.
"""

import sys
import os
from pathlib import Path
import subprocess

def main():
    """Main launcher function."""
    print("🚦 Vietnamese Traffic Law QA System - Streamlit Launcher")
    print("=" * 55)
    
    # Set up paths
    current_dir = Path(__file__).parent
    src_dir = current_dir / "src"
    streamlit_app = src_dir / "traffic_law_qa" / "ui" / "streamlit_app.py"
    
    # Check if streamlit app exists
    if not streamlit_app.exists():
        print(f"❌ Error: Streamlit app not found at {streamlit_app}")
        return 1
    
    # Check if data exists
    violations_path = current_dir / "data" / "processed" / "violations.json"
    if not violations_path.exists():
        print("⚠️ Warning: violations.json not found!")
        print(f"Expected at: {violations_path}")
        print("The app may not work properly without data.")
    else:
        print("✅ Data file found")
    
    # Set environment variable for Python path
    env = os.environ.copy()
    current_python_path = env.get('PYTHONPATH', '')
    if current_python_path:
        new_python_path = f"{src_dir}{os.pathsep}{current_python_path}"
    else:
        new_python_path = str(src_dir)
    
    env['PYTHONPATH'] = new_python_path
    
    print("🔄 Starting Streamlit...")
    print(f"📂 App location: {streamlit_app}")
    print("🌐 Open your browser to: http://localhost:8501")
    print("-" * 55)
    
    try:
        # Run streamlit with the correct environment
        cmd = [sys.executable, "-m", "streamlit", "run", str(streamlit_app)]
        subprocess.run(cmd, env=env, cwd=str(current_dir))
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down Streamlit...")
        return 0
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())