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


def setup() -> Settings:
    print("Hello there🫡... Let's setup your jira assistant.")

    jira_username = prompt("Please enter your Jira username 😎✌️: ").strip()
    jira_server = prompt("Please enter your jira server link 🔗🌐: ").strip()
    jira_api_token = prompt(
        "Please enter you Jira api-token 🤫🔑 (Get it from here: https://id.atlassian.com/manage-profile/security/api-tokens): \n").strip()

    try:
        jira = jira_auth(jira_username, jira_server, jira_api_token)
    except Exception as e:
        print(f"Sorry 😔. Failed to authenticate your jira identity due to {e}. Please try again")
        exit(1)

    settings = Settings(jira_username=jira_username, jira_token=jira_api_token, jira_server=jira_server)

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
            settings = Settings(**read_json(settings_path))
            jira_auth(settings.jira_username, server=settings.jira_server, api_key=settings.jira_token)
        except Exception as e:
            print(f"Sorry 😔. Failed to load settings due to: \n {str(e)}. \n Starting setup...\n")
            settings = setup()

    set_settings(settings)
    return settings
