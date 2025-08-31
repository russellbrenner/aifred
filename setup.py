#!/usr/bin/env python3

import os
import subprocess
import sys

def main():
    print("Setting up Aifred...")
    
    # Install requirements
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return
    
    # Make scripts executable
    scripts = ['aifred.py', 'alfred_filter.py', 'alfred_action.py']
    for script in scripts:
        os.chmod(script, 0o755)
        print(f"✅ Made {script} executable")
    
    print("\n🎉 Aifred setup complete!")
    print("\nNext steps:")
    print("1. Set your API keys in Alfred workflow variables:")
    print("   - OPENAI_API_KEY (for ChatGPT)")
    print("   - CLAUDE_API_KEY (for Claude)")
    print("2. Export your conversation data from ChatGPT/Claude")
    print("3. Use 'ai import' to import your conversations")
    print("4. Start searching with 'ai <query>'")

if __name__ == "__main__":
    main()