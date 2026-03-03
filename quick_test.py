"""
Quick test of the MSV prompts array function.
"""

from prompter import get_msv_prompts_array

def test_msv_array_function():
    """Test the convenience function for getting MSV prompts array."""
    
    print("=== MSV PROMPTS ARRAY FUNCTION TEST ===\n")
    
    # Test with file
    print("1. With CCJS file:")
    try:
        msv_prompts = get_msv_prompts_array("test_data/go-2025-4419.json")
        print(f"   ? Got {len(msv_prompts)} MSV prompts")
    except Exception as e:
        print(f"   ? Error: {e}")
    
    # Test without file
    print("\n2. Without file (general):")
    try:
        msv_prompts = get_msv_prompts_array()
        print(f"   ? Got {len(msv_prompts)} MSV prompts")
    except Exception as e:
        print(f"   ? Error: {e}")
    
    # Show first few prompts
    print(f"\n3. Sample prompts:")
    for i, prompt in enumerate(msv_prompts[:3], 1):
        print(f"   {i}. {prompt[:60]}...")
    
    print(f"\n? Function returns List[str] with {len(msv_prompts)} MSV validation prompts")
    print("Ready for your pipeline!")
    
    return msv_prompts

if __name__ == "__main__":
    test_msv_array_function()