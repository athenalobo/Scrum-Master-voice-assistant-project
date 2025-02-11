from pydantic import BaseModel

class Settings(BaseModel):
    jira_username: str
    jira_token: str
    jira_server: str
    project_keys: list = []