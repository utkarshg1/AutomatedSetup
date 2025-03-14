import os
import subprocess
import sys
from urllib.request import urlretrieve


def run_command(command, check=True, live_output=False):
    """Run a shell command with error handling and optional real-time output."""
    try:
        if live_output:
            # Run command and stream output directly
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=sys.stdout,
                stderr=sys.stderr,
                text=True,
            )
            process.communicate()
            if process.returncode != 0 and check:
                sys.exit(process.returncode)
        else:
            # Capture output normally
            result = subprocess.run(
                command,
                shell=True,
                check=check,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return result
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e.stderr}")
        sys.exit(1)


def check_gh_installed():
    """Verify GitHub CLI installation."""
    try:
        run_command("gh --version", check=False)
        return True
    except FileNotFoundError:
        print("✗ GitHub CLI not installed. Install from https://cli.github.com")
        return False


def github_auth():
    """Handle GitHub authentication."""
    result = run_command("gh auth status", check=False)
    if result.returncode != 0:
        print("🔑 Authenticating with GitHub...")
        run_command("gh auth login --web -h github.com", live_output=True)
    else:
        print("✓ GitHub authentication verified")


def create_github_repo(repo_name, visibility="public"):
    """Create GitHub repository in current directory."""
    print(f"🔄 Creating {visibility} repository '{repo_name}'...")
    try:
        # First commit all changes
        run_command("git add .")
        run_command('git commit -m "Initial commit"')

        # Create repo with source and remote flags
        run_command(
            f"gh repo create {repo_name} --{visibility} --source=. --remote=origin --push"
        )

        # Get GitHub username from authenticated user
        result = run_command("gh api user -q .login")
        github_username = result.stdout.strip()

        print(
            f"✓ GitHub repository created: https://github.com/{github_username}/{repo_name}"
        )
        return f"https://github.com/{github_username}/{repo_name}"
    except Exception as e:
        print(f"✗ Failed to create repository: {str(e)}")
        sys.exit(1)


def setup_git_config():
    """Set basic Git configuration if missing."""
    print("⚙️ Checking Git configuration...")
    if not run_command("git config user.name", check=False).stdout.strip():
        username = input("Enter your GitHub username: ").strip()
        run_command(f'git config user.name "{username}"')

    if not run_command("git config user.email", check=False).stdout.strip():
        email = input("Enter your GitHub email: ").strip()
        run_command(f'git config user.email "{email}"')


def initialize_local_repo():
    """Initialize Git repository in current directory."""
    if os.path.exists(".git"):
        print("✓ Git repository already exists")
        return

    print("🔄 Initializing local Git repository...")
    run_command("git init -b main")
    print("✓ Local Git repository initialized")


def download_files(url, filename):
    try:
        urlretrieve(url, filename)
        print(f"✓ File {filename} downloaded successfully")
    except Exception as e:
        print(f"✗ Failed to download {filename} : {str(e)}")


def create_basic_files():
    """Create essential project files if missing."""
    print("📂 Creating basic project structure...")

    if not os.path.exists(".gitignore"):
        gitignore_url = "https://raw.githubusercontent.com/github/gitignore/refs/heads/main/Python.gitignore"
        download_files(gitignore_url, ".gitignore")

    if not os.path.exists("LICENSE"):
        license_url = (
            "https://raw.githubusercontent.com/apache/.github/refs/heads/main/LICENSE"
        )
        download_files(license_url, "LICENSE")

    if not os.path.exists("README.md"):
        repo_name = os.path.basename(os.getcwd())
        with open("README.md", "w") as f:
            f.write(f"# {repo_name}\n\nProject description\n")
        print("✓ Created README.md")


def setup_virtualenv():
    """Create virtual environment, upgrade pip, and install requirements."""
    venv_dir = "venv"

    # Create virtual environment
    if not os.path.exists(venv_dir):
        print("\n🔄 Creating virtual environment...")
        run_command("python -m venv venv")
        print("✓ Virtual environment created")
    else:
        print("\n✓ Virtual environment already exists")

    # Determine activation command based on OS
    if sys.platform == "win32":
        activate_cmd = "call venv\\Scripts\\activate.bat"
    else:
        activate_cmd = "source venv/bin/activate"

    # Upgrade pip in activated environment
    print("\n🔄 Upgrading pip...")
    run_command(
        f"{activate_cmd} && python -m pip install --upgrade pip", live_output=True
    )
    print("✓ pip upgraded")

    # Install requirements if exists
    if os.path.exists("requirements.txt"):
        print("\n📦 Installing dependencies...")
        run_command(
            f"{activate_cmd} && pip install -r requirements.txt", live_output=True
        )
        print("✓ Dependencies installed")
    else:
        print("\nℹ️ No requirements.txt found - skipping dependency installation")

    # Print activation instructions
    print("\n🔌 Activate virtual environment with:")
    if sys.platform == "win32":
        print("  venv\\Scripts\\activate.bat")
    else:
        print("  source venv/bin/activate")


def main():
    print("🚀✨ Python Project Automation - Utkarsh Gaikwad ✨🚀")
    print("\n🚀 Project Setup Wizard - Current Directory\n")

    # Get user input
    repo_name = input("Enter GitHub repository name: ").strip()
    visibility = (
        input("Visibility [public/private] (default: public): ").strip().lower()
    )
    visibility = visibility if visibility in ["public", "private"] else "public"

    # Verify requirements
    if not check_gh_installed():
        sys.exit(1)

    # Setup Git
    setup_git_config()
    initialize_local_repo()

    # Create basic files
    create_basic_files()

    # GitHub setup
    github_auth()
    repo_url = create_github_repo(repo_name, visibility)

    # Setup venv
    setup_virtualenv()

    # Final output
    print("\n✅ Setup complete!")
    print(f"➤ Remote URL: {repo_url}")
    print(f"➤ Local directory: {os.getcwd()}")


if __name__ == "__main__":
    main()
