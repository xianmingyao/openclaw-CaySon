import sys
sys.path.insert(0, r'E:\workspace\skills\jingmai-putaway\jingmai-cli\resources\jingmai_product_publish\scripts')

try:
    import run_skill
    print("run_skill module loaded successfully")
    print(f"main function exists: {hasattr(run_skill, 'main')}")
    
    # Try calling main
    if hasattr(run_skill, 'main'):
        result = run_skill.main()
        print(f"main() returned: {result}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
