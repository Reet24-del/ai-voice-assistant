#!/usr/bin/env python3
"""
Error Simulation Script for Python Web App

This script helps test the robust error handling by temporarily disabling API keys.
It can comment/uncomment API keys in the .env file to simulate various failure scenarios.
"""

import os
import sys
import time
import shutil
from pathlib import Path

def backup_env_file():
    """Create a backup of the .env file"""
    env_file = Path(".env")
    if env_file.exists():
        backup_file = Path(".env.backup")
        shutil.copy2(env_file, backup_file)
        print(f"✅ Created backup: {backup_file}")
        return True
    else:
        print("❌ No .env file found!")
        return False

def restore_env_file():
    """Restore the .env file from backup"""
    backup_file = Path(".env.backup")
    if backup_file.exists():
        shutil.copy2(backup_file, Path(".env"))
        print("✅ Restored .env file from backup")
        return True
    else:
        print("❌ No backup file found!")
        return False

def disable_api_key(api_name):
    """Disable a specific API key by commenting it out"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ No .env file found!")
        return False
    
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    modified = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{api_name}_API_KEY=") and not line.strip().startswith("#"):
            lines[i] = f"# {line}"
            modified = True
            print(f"✅ Disabled {api_name} API key")
            break
    
    if modified:
        with open(env_file, 'w') as f:
            f.writelines(lines)
        return True
    else:
        print(f"⚠️ {api_name} API key not found or already disabled")
        return False

def enable_api_key(api_name):
    """Enable a specific API key by uncommenting it"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ No .env file found!")
        return False
    
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    modified = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f"# {api_name}_API_KEY="):
            lines[i] = line[2:]  # Remove the "# " prefix
            modified = True
            print(f"✅ Enabled {api_name} API key")
            break
    
    if modified:
        with open(env_file, 'w') as f:
            f.writelines(lines)
        return True
    else:
        print(f"⚠️ {api_name} API key not found or already enabled")
        return False

def disable_all_apis():
    """Disable all API keys to test complete fallback mode"""
    apis = ["MURF", "ASSEMBLYAI", "GEMINI"]
    for api in apis:
        disable_api_key(api)

def enable_all_apis():
    """Enable all API keys"""
    apis = ["MURF", "ASSEMBLYAI", "GEMINI"]
    for api in apis:
        enable_api_key(api)

def show_current_status():
    """Show current status of API keys"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ No .env file found!")
        return
    
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    print("\n📋 Current API Key Status:")
    print("=" * 40)
    
    apis = ["MURF", "ASSEMBLYAI", "GEMINI"]
    for api in apis:
        enabled = False
        disabled = False
        
        for line in lines:
            if line.strip().startswith(f"{api}_API_KEY=") and not line.strip().startswith("#"):
                enabled = True
                break
            elif line.strip().startswith(f"# {api}_API_KEY="):
                disabled = True
                break
        
        if enabled:
            print(f"✅ {api}: ENABLED")
        elif disabled:
            print(f"❌ {api}: DISABLED")
        else:
            print(f"❓ {api}: NOT FOUND")
    
    print("=" * 40)

def run_test_scenario(scenario_name, disable_apis, wait_time=10):
    """Run a specific test scenario"""
    print(f"\n🧪 Running Test Scenario: {scenario_name}")
    print("=" * 50)
    
    # Disable specified APIs
    for api in disable_apis:
        disable_api_key(api)
    
    print(f"\n⏳ Test scenario active for {wait_time} seconds...")
    print("🔄 You can now test your application to see fallback behavior")
    print("📱 Try the different features and observe the error handling")
    
    # Wait for the specified time
    for i in range(wait_time, 0, -1):
        print(f"⏰ {i} seconds remaining...", end="\r")
        time.sleep(1)
    
    print("\n\n🔄 Restoring API keys...")
    enable_all_apis()
    print(f"✅ Test scenario '{scenario_name}' completed")

def main():
    print("🛠️  Python Web App Error Simulation Tool")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("""
Usage: python simulate_errors.py <command>

Commands:
  backup          - Create backup of .env file
  restore         - Restore .env file from backup
  status          - Show current API key status
  disable-all     - Disable all API keys
  enable-all      - Enable all API keys
  disable <api>   - Disable specific API (murf, assemblyai, gemini)
  enable <api>    - Enable specific API
  test-scenarios  - Run automated test scenarios
  
Examples:
  python simulate_errors.py backup
  python simulate_errors.py disable murf
  python simulate_errors.py test-scenarios
  python simulate_errors.py status
  python simulate_errors.py restore
        """)
        return
    
    command = sys.argv[1].lower()
    
    if command == "backup":
        backup_env_file()
        
    elif command == "restore":
        restore_env_file()
        
    elif command == "status":
        show_current_status()
        
    elif command == "disable-all":
        if backup_env_file():
            disable_all_apis()
            show_current_status()
        
    elif command == "enable-all":
        enable_all_apis()
        show_current_status()
        
    elif command == "disable":
        if len(sys.argv) < 3:
            print("❌ Please specify API name: murf, assemblyai, or gemini")
            return
        api_name = sys.argv[2].upper()
        if api_name in ["MURF", "ASSEMBLYAI", "GEMINI"]:
            disable_api_key(api_name)
            show_current_status()
        else:
            print("❌ Invalid API name. Use: murf, assemblyai, or gemini")
            
    elif command == "enable":
        if len(sys.argv) < 3:
            print("❌ Please specify API name: murf, assemblyai, or gemini")
            return
        api_name = sys.argv[2].upper()
        if api_name in ["MURF", "ASSEMBLYAI", "GEMINI"]:
            enable_api_key(api_name)
            show_current_status()
        else:
            print("❌ Invalid API name. Use: murf, assemblyai, or gemini")
            
    elif command == "test-scenarios":
        print("\n🧪 Running Automated Test Scenarios")
        print("This will test different failure combinations...")
        
        # Create backup first
        if not backup_env_file():
            return
        
        try:
            # Test Scenario 1: TTS Service Failure
            run_test_scenario("TTS Service Failure", ["MURF"], 15)
            
            # Test Scenario 2: STT Service Failure  
            run_test_scenario("STT Service Failure", ["ASSEMBLYAI"], 15)
            
            # Test Scenario 3: LLM Service Failure
            run_test_scenario("LLM Service Failure", ["GEMINI"], 15)
            
            # Test Scenario 4: Multiple Service Failures
            run_test_scenario("Multiple Service Failures", ["MURF", "ASSEMBLYAI"], 20)
            
            # Test Scenario 5: Complete Fallback Mode
            run_test_scenario("Complete Fallback Mode", ["MURF", "ASSEMBLYAI", "GEMINI"], 25)
            
            print("\n🎉 All test scenarios completed!")
            print("📊 Your application should have demonstrated robust fallback behavior")
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Test interrupted by user")
            print("🔄 Restoring all API keys...")
            enable_all_apis()
            
        finally:
            show_current_status()
        
    else:
        print(f"❌ Unknown command: {command}")
        print("Run 'python simulate_errors.py' without arguments to see usage.")

if __name__ == "__main__":
    main()
