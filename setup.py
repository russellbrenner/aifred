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
    print("1) In Alfred → Workflows → Aifred → [i], set environment variables:")
    print("   - OPENAI_API_KEY (required for OpenAI)")
    print("   - ANTHROPIC_API_KEY (required for Anthropic)")
    print("   - Optional: AIFRED_PROVIDER_DEFAULT, AIFRED_MODEL_DEFAULT_OPENAI, AIFRED_MODEL_DEFAULT_ANTHROPIC")
    print("   - Optional: AIFRED_SYSTEM_PROMPT_PATH, AIFRED_DB_PATH, AIFRED_DRY_RUN=1")
    print("2) In Alfred, add a Script Filter node running: /usr/bin/python3 \"$PWD/alfred_filter.py\" \"{query}\"")
    print("3) Connect it to a Run Script node running: /usr/bin/python3 \"$PWD/alfred_action.py\" \"{query}\"")
    print("4) Type 'ai Hello @gpt-4o' in Alfred to send a message.")

if __name__ == "__main__":
    main()
