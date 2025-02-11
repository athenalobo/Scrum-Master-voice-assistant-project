import os
import tempfile
from typing import Optional
from prompt_toolkit import prompt
from file_utils import get_settings_path, write_json, write_file, is_file, read_json
from jira_utils import get_jira, jira_auth
from models.settings import Settings
settings: Optional[Settings] = None


def get_settings() -> Settings:
    return settings


def set_settings(settings: Settings):
    globals()["settings"] = settings


def get_all_project_keys(jira_client):
    try:
        projects = jira_client.projects()
        project_data = [(project.name, project.key) for project in projects]
        return sorted(project_data, key=lambda x: x[0])
    except Exception:
        return []


def save_project_keys_to_file(project_data):
    """Save project keys to a temporary file for user reference."""
    temp_file_path = os.path.join(tempfile.gettempdir(), 'jira_project_keys.txt')

    with open(temp_file_path, 'w') as f:
        f.write("Available Jira Project Keys:\n\n")
        for name, key in project_data:
            f.write(f"{name}: {key}\n")

    return temp_file_path


def setup() -> Settings:
    print("Welcome...🤗 Let's setup your Jira assistant.")

    jira_username = prompt("Please enter your Jira username (name@company.com) 👤: ").strip()
    jira_server = prompt("Please enter your Jira server link (https://your-domain.atlassian.net) 🔗🌐: ").strip()
    jira_api_token = prompt(
        "Please enter your Jira API token 🤫🔑 (Get it from here: https://id.atlassian.com/manage-profile/security/api-tokens): \n").strip()

    try:
        jira = jira_auth(jira_username, jira_server, jira_api_token)
    except Exception as e:
        print(f"Sorry 😔. Failed to authenticate your Jira identity due to {e}. Please try again.")
        exit(1)

    project_data = get_all_project_keys(jira)
    if not project_data:
        print("❗ Failed to fetch project keys. Please check your Jira credentials and try again.")
        exit(1)

    while True:
        print("\n📂 Please enter the project keys you want to use (comma-separated).")
        print("   Type 'ls' to see a list of available project keys.")
        project_keys_input = prompt("Project Keys: ").strip()

        if project_keys_input.lower() == 'ls':
            file_path = save_project_keys_to_file(project_data)
            clickable_path = f"\033]8;;file://{file_path}\033\\{file_path}\033]8;;\033\\"
            print(f"📝 List of Project Keys saved to: {clickable_path}")
            continue

        project_keys = [key.strip().upper() for key in project_keys_input.split(",")]
        valid_project_keys = [key for key in project_keys if any(key == project[1] for project in project_data)]

        if not valid_project_keys:
            print("❗ No valid project keys found. Please try again.")
        else:
            print(f"✅ Selected Project Keys: {', '.join(valid_project_keys)}")
            break

    settings = Settings(
        jira_username=jira_username,
        jira_token=jira_api_token,
        jira_server=jira_server,
        project_keys=valid_project_keys
    )

    set_settings(settings)

    try:
        settings_path = get_settings_path()
        write_json(settings_path, settings.dict())
        print(f"Successfully created settings at {settings_path} 😍✨")
    except Exception as e:
        print(f"Sorry 😔. Failed to create settings file due to {e}")
        exit(1)

    return settings


def load_settings() -> Settings:
    settings_path = get_settings_path()

    if not is_file(settings_path):
        settings = setup()
    else:
        try:
            settings_data = read_json(settings_path)
            if "project_keys" not in settings_data:
                settings_data["project_keys"] = []
            settings = Settings(**settings_data)
            jira_auth(settings.jira_username, server=settings.jira_server, api_key=settings.jira_token)
        except Exception as e:
            print(f"Sorry 😔. Failed to load settings due to: \n {str(e)}. \n Starting setup...\n")
            settings = setup()

    set_settings(settings)
    return settings
