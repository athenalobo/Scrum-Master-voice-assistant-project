import os
import json
import tempfile
import speech_recognition as sr
from jira import JIRA, JIRAError
import keyring

def validate_credentials(username, api_key):
    try:
        jira_client = JIRA(
            options={'server': 'https://cast-products.atlassian.net'},
            basic_auth=(username, api_key)
        )
        jira_client.current_user()
        return True
    except (JIRAError, Exception):
        return False

def load_credentials():
    username = keyring.get_password("jira", "username")
    api_key = keyring.get_password("jira", "api_key")
    
    if username and api_key:
        if validate_credentials(username, api_key):
            return username, api_key
        else:
            print("Authentication credentials are no longer valid!")
            keyring.delete_password("jira", "username")
            keyring.delete_password("jira", "api_key")
    
    while True:
        username = input("Enter Jira username: ")
        api_key = input("Enter Jira API token: ")
        
        if validate_credentials(username, api_key):
            keyring.set_password("jira", "username", username)
            keyring.set_password("jira", "api_key", api_key)
            return username, api_key
        else:
            print("Invalid credentials. Please try again.")

def get_user_id(jira_client, user_display_name):
    users = jira_client.search_users(query=user_display_name, maxResults=1)
    for user in users:
        if user.displayName.lower() == user_display_name.lower():
            return user.accountId
    raise ValueError(f"User '{user_display_name}' not found in Jira.")

def confirm_input(text):
    print(f"Heard: {text}")
    while True:
        confirmation = input("Is this correct? (Y/N): ").lower()
        if confirmation == 'y':
            return text
        elif confirmation == 'n':
            return input("Please type the correct text: ")
        else:
            print("Please enter Y or N.")

def listen(prompt):
    recognizer = sr.Recognizer()
    while True:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print(prompt)
            audio = recognizer.listen(source, timeout=5)
        
        try:
            result = recognizer.recognize_google(audio).lower()
            confirmed_result = confirm_input(result)
            return confirmed_result
        except sr.UnknownValueError:
            print("Could not understand. Please try again.")

def choose_from_options(prompt, options):
    print(prompt)
    for key, option in enumerate(options, 1):
        print(f"{key}. {option}")
    
    while True:
        try:
            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def get_all_project_keys(jira_client):
    try:
        projects = jira_client.projects()
        project_data = [(project.name, project.key) for project in projects]
        return sorted(project_data, key=lambda x: x[0])
    except JIRAError as e:
        print(f"Error retrieving project keys: {e}")
        return []

def save_project_keys_to_file(project_data):
    temp_file_path = os.path.join(tempfile.gettempdir(), 'jira_project_keys.txt')
    
    with open(temp_file_path, 'w') as f:
        f.write("CAST Jira Project Keys:\n\n")
        for name, key in project_data:
            f.write(f"{name}: {key}\n")
    
    return temp_file_path

def create_ticket():
    try:
        username, api_key = load_credentials()
        
        jira_client = JIRA(
            options={'server': 'https://cast-products.atlassian.net'},
            basic_auth=(username, api_key)
        )

        projects = ['Imaging Cloud', 'Profiler', 'Other']
        project = choose_from_options("Choose Project:", projects)

        product_owners = {
            'Damien Charlemagne': None,
            'Guillaume Rager': None,
            'Anshu Sharma': None,
            'Arnaud Garnier': None,
            'Samy Bouachour': None
        }

        for po in product_owners:
            product_owners[po] = get_user_id(jira_client, po)

        if project == 'Imaging Cloud':
            product_owner_id = product_owners['Damien Charlemagne']
            project_key = 'IMAGLITE'
        elif project == 'Profiler':
            product_owner_id = product_owners['Guillaume Rager']
            project_key = 'PROFILER'
        else:
            while True:
                project_key_input = input("Enter the project key (type 'ls' to see list): ")
                
                if project_key_input.lower() == 'ls':
                    project_data = get_all_project_keys(jira_client)
                    
                    if project_data:
                        file_path = save_project_keys_to_file(project_data)
                        print(f"List of Project Keys: {file_path}")
                    else:
                        print("No project keys could be retrieved.")
                
                else:
                    project_key = project_key_input.upper()
                    break
                
            product_owner = choose_from_options("Select Product Owner:", list(product_owners.keys()))
            product_owner_id = product_owners[product_owner]

        issue_types = ['Story', 'Technical Story', 'Bug']
        issue_type = choose_from_options("Choose Issue Type:", issue_types).lower()
        
        summary = listen("What is the summary?")
        description = listen("What is the description?")

        issue_dict = {
            'project': {'key': project_key},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issue_type.title()},
            'customfield_10101': {'accountId': product_owner_id},
        }

        if issue_type == 'bug':
            priorities = ['Minor', 'Major', 'Critical', 'Blocker']
            priority = choose_from_options("Choose Priority:", priorities).lower()
            
            issue_dict['priority'] = {'name': priority.capitalize()}
            issue_dict['customfield_10175'] = '-'

        new_issue = jira_client.create_issue(fields=issue_dict)
        ticket_url = f"https://cast-products.atlassian.net/browse/{new_issue.key}"
        print(f"Ticket created successfully: {ticket_url}")

    except JIRAError as e:
        print(f"Unexpected error creating ticket: {e}")

def main():
    create_ticket()

if __name__ == "__main__":
    main()