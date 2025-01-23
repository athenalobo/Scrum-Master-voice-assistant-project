import os
import json
import speech_recognition as sr
from jira import JIRA, JIRAError
import keyring

def load_credentials():
    username = keyring.get_password("jira", "username")
    api_key = keyring.get_password("jira", "api_key")
    
    if not username or not api_key:
        username = input("Enter Jira username: ")
        api_key = input("Enter Jira API key: ")
        
        keyring.set_password("jira", "username", username)
        keyring.set_password("jira", "api_key", api_key)
    
    return username, api_key

def validate_jira_credentials(username, api_key):
    try:
        JIRA(
            options={'server': 'https://cast-products.atlassian.net'},
            basic_auth=(username, api_key)
        )
        return True
    except JIRAError:
        return False

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

def create_ticket():
    try:
        username, api_key = load_credentials()
        
        jira_client = JIRA(
            options={'server': 'https://cast-products.atlassian.net'},
            basic_auth=(username, api_key)
        )

        projects = ['Imaging Cloud', 'Profiler']
        project = choose_from_options("Choose Project:", projects)
        
        product_owner_mapping = {
            'Imaging Cloud': '557058:b7a5cd30-61eb-4bab-99b5-158c8abcf1f9',
            'Profiler': '70121:c059206c-fc48-4dea-a202-8096c51fe619'
        }
        
        project_name_mapping = {
            'Imaging Cloud': 'IMAGLITE',
            'Profiler': 'PROFILER'
        }

        issue_types = ['Story', 'Technical Story', 'Bug']
        issue_type = choose_from_options("Choose Issue Type:", issue_types).lower()
        
        summary = listen("What is the summary?")
        description = listen("What is the description?")

        issue_dict = {
            'project': {'key': project_name_mapping[project]},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issue_type.title()},
            'customfield_10101': {'accountId': product_owner_mapping[project]},
        }

        if issue_type == 'bug':
            priorities = ['Minor', 'Major', 'Critical', 'Blocker']
            priority = choose_from_options("Choose Priority:", priorities).lower()
            
            issue_dict['priority'] = {'name': priority.capitalize()}
            issue_dict['customfield_10175'] = '-'

        new_issue = jira_client.create_issue(fields=issue_dict)
        ticket_url = f"https://cast-products.atlassian.net/browse/{new_issue.key}"
        print(f"Ticket created successfully: {new_issue.key}")
        print(f"Ticket URL: {ticket_url}")

    except JIRAError as e:
        
        if e.status_code == 401 or "permission" in str(e).lower():
            print("Authentication or permission issue detected.")
            print("Please re-enter your Jira credentials.")
            
            keyring.delete_password("jira", "username")
            keyring.delete_password("jira", "api_key")
            
            username = input("Enter Jira username: ")
            api_key = input("Enter Jira API key: ")
            
            keyring.set_password("jira", "username", username)
            keyring.set_password("jira", "api_key", api_key)
            
            try:
                jira_client = JIRA(
                    options={'server': 'https://cast-products.atlassian.net'},
                    basic_auth=(username, api_key)
                )
                
                new_issue = jira_client.create_issue(fields=issue_dict)
                ticket_url = f"https://cast-products.atlassian.net/browse/{new_issue.key}"
                print(f"Ticket created successfully: {new_issue.key}")
                print(f"Ticket URL: {ticket_url}")
            
            except JIRAError as retry_error:
                print(f"Failed to create ticket after re-entering credentials: {retry_error}")
        else:
            print(f"Unexpected error creating ticket: {e}")

def main():
    create_ticket()

if __name__ == "__main__":
    main()