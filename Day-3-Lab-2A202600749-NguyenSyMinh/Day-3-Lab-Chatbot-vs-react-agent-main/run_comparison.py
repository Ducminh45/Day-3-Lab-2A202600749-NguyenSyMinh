import os
import subprocess
import sys

# Reconfigure stdout to use UTF-8 to handle Vietnamese text without crashing on Windows terminal
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("=" * 60)
    print("  CHATBOT VS REACT AGENT SYSTEM COMPARISON RUNNER  ")
    print("=" * 60)
    
    # Path to test_comparison.py
    test_path = os.path.join("tests", "test_comparison.py")
    
    if not os.path.exists(test_path):
        print(f"[ERROR] Could not find test file at {test_path}")
        return
        
    print(f"[INFO] Executing system evaluation suite from {test_path}...")
    
    try:
        # Run test_comparison.py using python interpreter
        result = subprocess.run([sys.executable, test_path], check=True)
        if result.returncode == 0:
            print("\n[SUCCESS] Comparison test suite executed successfully!")
            print("[INFO] Please check 'report/comparison_report.md' for the detailed report.")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Comparison test suite failed during execution: {e}")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
