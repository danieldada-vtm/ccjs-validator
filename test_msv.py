"""
Test MSV Prompter - Shows actual string arrays for pipeline integration.
"""

from prompter import CCJSMSVPrompter, create_msv_prompter_from_file


def show_msv_prompt_array():
    """Display the actual MSV validation prompt array for your ingestion pipeline."""
    
    print("=== MSV VALIDATION PROMPT ARRAY ===\n")
    
    # Create MSV prompter
    try:
        prompter = create_msv_prompter_from_file("test_data/go-2025-4419.json")
        print(f"? Using CCJS RIN {prompter.report.go.rin} for MSV validation")
    except:
        prompter = CCJSMSVPrompter()
        print("? Using general MSV prompter")
    
    # Get the main MSV validation prompts array
    print("\nMSV VALIDATION PROMPTS - Array of Strings:")
    msv_prompts = prompter.generate_msv_validation_prompts()
    
    for i, prompt in enumerate(msv_prompts):
        print(f"[{i}]: \"{prompt}\"")
    
    print(f"\nArray Details:")
    print(f"  Type: {type(msv_prompts)}")
    print(f"  Length: {len(msv_prompts)} strings")
    
    print(f"\nPipeline Usage:")
    print("```python")
    print("from prompter import CCJSMSVPrompter")
    print("")
    print("# Create MSV prompter")
    print("prompter = CCJSMSVPrompter()")
    print("")
    print("# Get MSV validation prompts array")
    print("msv_prompts = prompter.generate_msv_validation_prompts()")
    print("")
    print("# Feed array to your ingestion pipeline")
    print("for prompt in msv_prompts:")
    print("    result = your_pipeline.validate_msv(prompt, ccjs_data)")
    print("    # Process result...")
    print("```")
    
    return msv_prompts


def show_all_msv_categories():
    """Show all MSV prompt categories available."""
    
    prompter = CCJSMSVPrompter()
    
    print(f"\n=== ALL MSV PROMPT CATEGORIES ===")
    all_prompts = prompter.generate_all_msv_prompts()
    
    for category, prompts in all_prompts.items():
        print(f"\n{category.upper().replace('_', ' ')}:")
        print(f"  Function: prompter.{category.replace('msv_', 'generate_msv_')}()")
        print(f"  Count: {len(prompts)} prompts")
        
        # List all prompts in this category
        for i, prompt in enumerate(prompts, 1):
            print(f"  [{i}]: \"{prompt}\"")
    
    total_prompts = sum(len(prompts) for prompts in all_prompts.values())
    print(f"\nTotal MSV prompts across all categories: {total_prompts}")


if __name__ == "__main__":
    msv_array = show_msv_prompt_array()
    show_all_msv_categories()
    
    print(f"\n=== SUMMARY ===")
    print(f"? MSV validation prompts: {len(msv_array)} strings")
    print(f"? Covers: incident date, completion status, weapon compatibility,")
    print(f"   victim requirements, age restrictions, relationships, injury compatibility")
    print(f"? Ready for your MSV validation pipeline!")