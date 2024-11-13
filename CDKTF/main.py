import typer
import os
from dotenv import load_dotenv
from typing_extensions import Annotated

app = typer.Typer()
library_path = '/workspaces/dtr-validations/analytics/'
dotenv_path = '/workspaces/dtr-validations/validator/.env'
load_dotenv(dotenv_path)

# ANSI escape sequences for different colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def list_subdirectories():
    path = f"{library_path}"
    # Get list of all subdirectories
    subdirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    # Define the path
    return subdirs

@app.command()
def active():
    """
    Displays the active validation module.
    """
    ## Retrieve environemnt variable $VALIDATION_ENV from .env
    active_env=os.getenv('VALIDATION_ENV')
    # Color coded responses
    if not active_env:
        print(f"{YELLOW}[ACTIVE]{RESET} {RED}{active_env}{RESET}" )
    else:
        print(f"{YELLOW}[ACTIVE]{RESET} {GREEN}{active_env}{RESET}" )

@app.command()
def select(
    # Autocomplete analytic module list using subdirs of /analytics folder
    module: Annotated[
        str, typer.Option(help="Select an Analytic Module", autocompletion=list_subdirectories)
    ],
    ):
    """
    Selects a validation module to activate.
    """
    # Check if .env exists, if not, create one.
    file_path = f"{dotenv_path}"
    if not os.path.exists(file_path):
        open(".env", "w")
    # Change PWD to active module's path
    active_module_path = f"{library_path}{module}"
    if os.path.exists(active_module_path):
        os.system("unset VALIDATION_ENV")
        # Change PWD of session
        os.chdir(active_module_path)
        # Export valid module as env variable
        os.system(f"echo VALIDATION_ENV='{module}' > {dotenv_path}")
    else:
        # Error message for non-existent module
        print(f"{RED}[ERROR]{RESET} Module Does Not Exist!")

@app.command()
def deploy():
    """
    Deploys active validation module.
    """
    env = os.getenv("VALIDATION_ENV")
    module_path = f"{library_path}{env}"
    if os.path.exists(module_path):
        # Change PWD of session
        os.chdir(active_module_path)
        os.system("bash validation_script.sh")
    else:
        # Error message for non-existent module
        print(f"{RED}[ERROR]{RESET} Module Does Not Exist!")

@app.command()
def destroy():
    """
    Reverts validation module changes.
    """
    env = os.getenv("VALIDATION_ENV")
    module_path = f"{library_path}{env}"
    if os.path.exists(module_path):
        # Change PWD of session
        os.chdir(active_module_path)
        os.system("cdktf destroy")
    else:
        print(f"{RED}[ERROR]{RESET} Module Does Not Exist!")

@app.command()
def reset():
    """
    Resets CLI and active environment.
    """
    open(".env", "w")
    home_dir = f"{library_path}"
    os.chdir(f"{home_dir}")
    print(f"{GREEN}Active module cleared!{RESET}")

@app.command()
def diff():
    """
    Creates an execution plan, which lets you preview the changes that Terraform plans to make to your infrastructure.
    """
    env = os.getenv("VALIDATION_ENV")
    module_path = f"{library_path}{env}"
    if os.path.exists(module_path):
        # Change PWD of session
        os.chdir(active_module_path)
        os.system("cdktf diff")
    else:
        print(f"{RED}[ERROR]{RESET} Module Does Not Exist!")

@app.command()
def synth():
    """
    Synthesizes Terraform code for the given app in a directory.
    """
    env = os.getenv("VALIDATION_ENV")
    module_path = f"{library_path}{env}"
    if os.path.exists(module_path):
        # Change PWD of session
        os.chdir(active_module_path)
        os.system("cdktf synth")
    else:
        print(f"{RED}[ERROR]{RESET} Module Does Not Exist!")

if __name__ == "__main__":
    app()
