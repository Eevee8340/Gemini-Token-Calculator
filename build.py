import os
import subprocess
import sys
from pathlib import Path

def main():
    # Define paths
    base_dir = Path(__file__).parent.resolve()
    main_script = base_dir / "src" / "main.py"
    
    print("Building gemini-token-calculator executable with PyInstaller...")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "gemini-token-calculator",
        "--onefile",
        "--clean",
        "--noconfirm",
        str(main_script)
    ]
    
    try:
        subprocess.run(cmd, check=True, cwd=base_dir)
        print("\n[SUCCESS] Build successful!")
        print(f"Executable can be found in the 'dist' directory: {base_dir / 'dist'}")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
