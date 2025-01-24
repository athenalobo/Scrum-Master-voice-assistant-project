from typing import Optional

from jira import JIRA

jira: Optional[JIRA] = None


def get_jira():
    return jira


def set_jira(jira: JIRA):
    globals()['jira'] = jira


def jira_auth(username: str, server: str, api_key: str) -> Optional[JIRA]:
    jira = JIRA(server=server, basic_auth=(username, api_key))

    jira.current_user()
    set_jira(jira)

    return jira
