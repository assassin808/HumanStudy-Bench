"""
Quick test with your OpenRouter API key
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_api_key():
    """Test if the API key works with a simple call"""
    
    api_key = "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"
    
    print("="*70)
    print("Testing OpenRouter API Key")
    print("="*70)
    print(f"\nAPI Key: {api_key[:20]}...")
    print(f"Model: mistralai/mistral-nemo")
    print(f"API Base: https://openrouter.ai/api/v1")
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        print("\n🔄 Making test API call...")
        
        response = client.chat.completions.create(
            model="mistralai/mistral-nemo",
            messages=[
                {"role": "user", "content": "Say 'Hello, HumanStudyBench!' in one sentence."}
            ],
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        
        print("\n✅ API call successful!")
        print(f"\nResponse: {result}")
        print(f"\nUsage:")
        print(f"  Prompt tokens: {response.usage.prompt_tokens}")
        print(f"  Completion tokens: {response.usage.completion_tokens}")
        print(f"  Total tokens: {response.usage.total_tokens}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ API call failed: {e}")
        return False


if __name__ == "__main__":
    success = test_api_key()
    
    if success:
        print("\n" + "="*70)
        print("✅ Your API key is working!")
        print("="*70)
        print("\n🚀 You can now run:")
        print("   python examples/40_openrouter_demo.py")
        print("\nOr set it as environment variable:")
        print("   export OPENROUTER_API_KEY='sk-or-v1-...'")
    else:
        print("\n" + "="*70)
        print("⚠️  API key test failed")
        print("="*70)
        print("\nPlease check:")
        print("1. Is the API key valid?")
        print("2. Do you have credits on OpenRouter?")
        print("3. Is your internet connection working?")
