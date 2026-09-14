"""
Setup and environment installer for Classical Maze - Search Algorithm Race.
Checks Python version, optionally creates/activates a virtual environment,
installs dependencies, and provides options to launch or test the simulation.
"""
import os
import sys
import subprocess
import shutil

MIN_PYTHON_VERSION = (3, 8)
REQUIREMENTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
VENV_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv")

def print_header(title: str):
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def check_python_version():
    cur = sys.version_info
    print(f"[*] Detected Python: {cur.major}.{cur.minor}.{cur.micro}")
    if cur < MIN_PYTHON_VERSION:
        print(f"[!] Error: Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+ is required.")
        sys.exit(1)
    print("[+] Python version is compatible.")

def get_venv_python_and_pip():
    is_win = sys.platform.startswith("win")
    if is_win:
        venv_python = os.path.join(VENV_DIR, "Scripts", "python.exe")
        venv_pip = os.path.join(VENV_DIR, "Scripts", "pip.exe")
    else:
        venv_python = os.path.join(VENV_DIR, "bin", "python")
        venv_pip = os.path.join(VENV_DIR, "bin", "pip")
    return venv_python, venv_pip

def create_virtualenv():
    venv_python, _ = get_venv_python_and_pip()
    if os.path.exists(venv_python):
        print(f"[+] Virtual environment already exists at: {VENV_DIR}")
        return venv_python

    print(f"[*] Creating virtual environment in '{VENV_DIR}'...")
    try:
        subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])
        print("[+] Virtual environment created successfully.")
        return venv_python
    except subprocess.CalledProcessError as err:
        print(f"[!] Warning: Failed to create virtual environment: {err}")
        print("[*] Proceeding with the current Python environment.")
        return sys.executable

def install_requirements(python_bin: str):
    print_header("Installing Required Dependencies")
    if not os.path.exists(REQUIREMENTS_FILE):
        print(f"[!] Error: {REQUIREMENTS_FILE} not found.")
        sys.exit(1)

    print(f"[*] Upgrading pip and installing packages using: {python_bin}")
    try:
        subprocess.check_call([python_bin, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([python_bin, "-m", "pip", "install", "-r", REQUIREMENTS_FILE])
        print("\n[+] All dependencies installed successfully!")
    except subprocess.CalledProcessError as err:
        print(f"\n[!] Error during package installation: {err}")
        sys.exit(1)

def verify_installation(python_bin: str):
    print_header("Verifying Installation")
    code = (
        "import pygame; "
        "import config, maze, world, agent, renderer, ui; "
        "import searches; "
        "print(f'[+] Pygame {pygame.__version__} and all game modules loaded successfully.')"
    )
    try:
        subprocess.check_call([python_bin, "-c", code], cwd=os.path.dirname(os.path.abspath(__file__)))
    except subprocess.CalledProcessError as err:
        print(f"[!] Verification failed: {err}")
        sys.exit(1)

def print_next_steps(python_bin: str):
    print_header("Setup Complete!")
    is_win = sys.platform.startswith("win")
    activate_cmd = ".\\.venv\\Scripts\\activate" if is_win else "source .venv/bin/activate"

    print("To run the Classical Maze - Search Algorithm Race:\n")
    print("Option 1 (Direct launch using the venv python):")
    print(f"   {python_bin} main.py\n")
    print("Option 2 (Activate virtual environment, then launch):")
    print(f"   {activate_cmd}")
    print("   python main.py\n")
    print("Controls:")
    print("   [SPACE]     : Pause / Resume")
    print("   [R]         : Reset / Generate new maze and race")
    print("   [TAB]       : Toggle search expansion visualization")
    print("   [+] / [-]   : Increase / Decrease agent movement speed")
    print("   [0] - [7]   : Focus on specific algorithm (0: All, 1-7: Single Agent)")
    print("   [ESC]       : Quit")
    print("=" * 60)

def main():
    print_header("Classical Maze - Setup & Installation")
    check_python_version()

    # Ask user whether to create venv or install directly if interactive, else default to venv
    use_venv = True
    python_bin = create_virtualenv() if use_venv else sys.executable

    install_requirements(python_bin)
    verify_installation(python_bin)
    print_next_steps(python_bin)

    if "--run" in sys.argv:
        print("\n[*] Launching simulation now...")
        subprocess.call([python_bin, "main.py"], cwd=os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    main()
