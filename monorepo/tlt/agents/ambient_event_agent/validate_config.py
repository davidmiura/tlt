#!/usr/bin/env python3
"""Configuration validation script for Ambient Event Agent"""

import json
import sys
import argparse
from typing import Dict, Any, List
import requests
from urllib.parse import urljoin

def validate_json_syntax(config_path: str) -> Dict[str, Any]:
    """Validate JSON syntax and load configuration"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"✅ JSON syntax valid: {config_path}")
        return config
    except json.JSONDecodeError as e:
        print(f"❌ JSON syntax error in {config_path}: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_path}")
        sys.exit(1)

def validate_required_fields(config: Dict[str, Any]) -> None:
    """Validate required configuration fields"""
    required_fields = [
        'agent_id',
        'mcp_services',
        'adapter_services',
        'agent_config'
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in config:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ Missing required fields: {missing_fields}")
        sys.exit(1)
    else:
        print("✅ All required fields present")

def check_service_connectivity(url: str, service_name: str, timeout: int = 5) -> bool:
    """Check if a service is accessible"""
    try:
        # Try common health check endpoints
        health_endpoints = ['/health', '/status', '/', '/mcp']
        
        for endpoint in health_endpoints:
            try:
                full_url = urljoin(url, endpoint)
                response = requests.get(full_url, timeout=timeout)
                if response.status_code in [200, 404]:  # 404 is OK for service existence
                    print(f"✅ {service_name} accessible at {url}")
                    return True
            except requests.RequestException:
                continue
        
        print(f"⚠️  {service_name} not accessible at {url}")
        return False
        
    except Exception as e:
        print(f"⚠️  Error checking {service_name} at {url}: {e}")
        return False

def validate_mcp_services(config: Dict[str, Any]) -> List[str]:
    """Validate MCP service configurations"""
    mcp_services = config.get('mcp_services', {})
    accessible_services = []
    
    print("\n🔍 Checking MCP Services:")
    
    for service_name, service_config in mcp_services.items():
        url = service_config.get('url')
        if not url:
            print(f"❌ {service_name}: Missing URL")
            continue
            
        enabled = service_config.get('enabled', True)
        if not enabled:
            print(f"⏸️  {service_name}: Disabled in config")
            continue
            
        if check_service_connectivity(url, service_name):
            accessible_services.append(service_name)
        
        # Validate tools list
        tools = service_config.get('tools', [])
        if tools:
            print(f"   📋 {len(tools)} tools configured")
        else:
            print(f"   ⚠️  No tools specified")
    
    return accessible_services

def validate_adapter_services(config: Dict[str, Any]) -> List[str]:
    """Validate adapter service configurations"""
    adapter_services = config.get('adapter_services', {})
    accessible_services = []
    
    print("\n🔍 Checking Adapter Services:")
    
    for service_name, service_config in adapter_services.items():
        url = service_config.get('url')
        if not url:
            print(f"❌ {service_name}: Missing URL")
            continue
            
        enabled = service_config.get('enabled', True)
        if not enabled:
            print(f"⏸️  {service_name}: Disabled in config")
            continue
            
        if check_service_connectivity(url, service_name):
            accessible_services.append(service_name)
    
    return accessible_services

def validate_agent_config(config: Dict[str, Any]) -> None:
    """Validate agent-specific configuration"""
    agent_config = config.get('agent_config', {})
    
    print("\n🔍 Checking Agent Configuration:")
    
    # Check numeric values
    numeric_fields = {
        'max_pending_events': (1, 1000),
        'max_conversation_history': (10, 10000),
        'timer_check_interval': (1, 3600),
        'max_retry_attempts': (1, 10),
        'message_rate_limit': (1, 100)
    }
    
    for field, (min_val, max_val) in numeric_fields.items():
        value = agent_config.get(field)
        if value is not None:
            if min_val <= value <= max_val:
                print(f"✅ {field}: {value}")
            else:
                print(f"⚠️  {field}: {value} (recommended range: {min_val}-{max_val})")
        else:
            print(f"⚠️  {field}: Not specified")

def validate_timer_settings(config: Dict[str, Any]) -> None:
    """Validate timer configuration"""
    timer_settings = config.get('timer_settings', {})
    reminder_schedule = timer_settings.get('reminder_schedule', {})
    
    print("\n🔍 Checking Timer Settings:")
    
    expected_timers = ['1_day_before', 'day_of', 'event_time', 'followup']
    
    for timer_name in expected_timers:
        timer_config = reminder_schedule.get(timer_name)
        if timer_config:
            enabled = timer_config.get('enabled', False)
            minutes = timer_config.get('minutes_before_event') or timer_config.get('minutes_after_event')
            status = "✅" if enabled else "⏸️ "
            print(f"{status} {timer_name}: {minutes} minutes, enabled={enabled}")
        else:
            print(f"⚠️  {timer_name}: Not configured")

def validate_discord_settings(config: Dict[str, Any]) -> None:
    """Validate Discord configuration"""
    discord_settings = config.get('discord_settings', {})
    
    print("\n🔍 Checking Discord Settings:")
    
    # Check channel ID format
    default_channel = discord_settings.get('default_channel_id')
    if default_channel:
        if isinstance(default_channel, str) and len(default_channel) >= 17:
            print(f"✅ Default channel ID: {default_channel}")
        else:
            print(f"⚠️  Default channel ID format may be invalid: {default_channel}")
    else:
        print("⚠️  No default channel ID specified")
    
    # Check rate limiting
    rate_limiting = discord_settings.get('rate_limiting', {})
    messages_per_minute = rate_limiting.get('messages_per_minute', 0)
    if 1 <= messages_per_minute <= 60:
        print(f"✅ Rate limit: {messages_per_minute} messages/minute")
    else:
        print(f"⚠️  Rate limit may be too high or low: {messages_per_minute}")

def validate_openai_key(config: Dict[str, Any]) -> None:
    """Validate OpenAI API key"""
    api_key = config.get('openai_api_key')
    
    print("\n🔍 Checking OpenAI Configuration:")
    
    if not api_key:
        print("⚠️  No OpenAI API key specified (will use environment variable)")
    elif api_key == "dummy-key-for-testing":
        print("⚠️  Using dummy API key (testing mode)")
    elif api_key.startswith('sk-'):
        print("✅ OpenAI API key format looks valid")
    else:
        print("⚠️  OpenAI API key format may be invalid")

def generate_summary(accessible_mcp: List[str], accessible_adapters: List[str]) -> None:
    """Generate validation summary"""
    print("\n" + "="*50)
    print("📊 VALIDATION SUMMARY")
    print("="*50)
    
    print(f"✅ Accessible MCP Services: {len(accessible_mcp)}")
    for service in accessible_mcp:
        print(f"   • {service}")
    
    print(f"✅ Accessible Adapter Services: {len(accessible_adapters)}")
    for service in accessible_adapters:
        print(f"   • {service}")
    
    total_services = len(accessible_mcp) + len(accessible_adapters)
    if total_services >= 3:
        print("\n🎉 Configuration looks good! Ready to run the agent.")
    elif total_services >= 1:
        print("\n⚠️  Some services are not accessible. Agent will run with limited functionality.")
    else:
        print("\n❌ No services accessible. Please start the required services first.")

def main():
    parser = argparse.ArgumentParser(description="Validate Ambient Event Agent configuration")
    parser.add_argument(
        'config_file',
        nargs='?',
        default='test_config.json',
        help='Path to configuration file (default: test_config.json)'
    )
    parser.add_argument(
        '--skip-connectivity',
        action='store_true',
        help='Skip service connectivity checks'
    )
    
    args = parser.parse_args()
    
    print("🔍 Validating Ambient Event Agent Configuration")
    print("=" * 50)
    
    # Validate JSON syntax and load config
    config = validate_json_syntax(args.config_file)
    
    # Validate required fields
    validate_required_fields(config)
    
    # Validate agent configuration
    validate_agent_config(config)
    
    # Validate timer settings
    validate_timer_settings(config)
    
    # Validate Discord settings
    validate_discord_settings(config)
    
    # Validate OpenAI configuration
    validate_openai_key(config)
    
    accessible_mcp = []
    accessible_adapters = []
    
    if not args.skip_connectivity:
        # Check service connectivity
        accessible_mcp = validate_mcp_services(config)
        accessible_adapters = validate_adapter_services(config)
    else:
        print("\n⏸️  Skipping connectivity checks")
    
    # Generate summary
    generate_summary(accessible_mcp, accessible_adapters)

if __name__ == "__main__":
    main()