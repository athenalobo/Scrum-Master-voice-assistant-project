import os
from dotenv import load_dotenv
import speech_recognition as sr
from jira import JIRA
import time

# Load environment variables from .env file
load_dotenv()

class JiraVoiceTicketCreator:
    def __init__(self):
        self.jira_client = JIRA(
            options={'server': os.getenv('JIRA_SERVER')},
            basic_auth=(
                os.getenv('JIRA_USERNAME'), 
                os.getenv('JIRA_PASSWORD')
            )
        )
        self.recognizer = sr.Recognizer()
   
    def confirm_input(self, text):
        print(f"Heard: {text}")
        while True:
            confirmation = input("Is this correct? (Y/N): ").lower()
            if confirmation == 'y':
                return text
            elif confirmation == 'n':
                return input("Please type the correct text: ")
            else:
                print("Please enter Y or N.")
   
    def listen(self, prompt):
        while True:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print(prompt)
                audio = self.recognizer.listen(source, timeout=5)
           
            try:
                result = self.recognizer.recognize_google(audio).lower()
                confirmed_result = self.confirm_input(result)
                return confirmed_result
            except sr.UnknownValueError:
                print("Could not understand. Please try again.")
   
    def choose_from_options(self, prompt, options):
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
   
    def create_ticket(self):
        projects = ['Imaging Cloud', 'Profiler']
        project = self.choose_from_options(
            "Choose Project:",
            projects
        )
       
        custom_field_mapping = {
            'Imaging Cloud': '557058:b7a5cd30-61eb-4bab-99b5-158c8abcf1f9',
            'Profiler': '70121:c059206c-fc48-4dea-a202-8096c51fe619'
        }
       
        project_name_mapping = {
            'Imaging Cloud': 'IMAGLITE',
            'Profiler': 'PROFILER'
        }
       
        issue_types = ['Story', 'Technical Story', 'Bug']
        issue_type = self.choose_from_options(
            "Choose Issue Type:",
            issue_types
        ).lower()
       
        summary = self.listen("What is the summary?")
        description = self.listen("What is the description?")
       
        issue_dict = {
            'project': {'key': project_name_mapping[project]},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issue_type.title()},
            'customfield_10101': {'accountId': custom_field_mapping[project]}
        }
       
        if issue_type == 'bug':
            priorities = ['Minor', 'Major', 'Critical', 'Blocker']
            priority = self.choose_from_options(
                "Choose Priority:",
                priorities
            ).lower()
           
            issue_dict['priority'] = {'name': priority.capitalize()}
            issue_dict['customfield_10175'] = '-'
       
        try:
            new_issue = self.jira_client.create_issue(fields=issue_dict)
            print(f"Ticket created successfully: {new_issue.key}")
        except Exception as e:
            print(f"Error creating ticket: {e}")

# Usage
if __name__ == "__main__":
    voice_creator = JiraVoiceTicketCreator()
    voice_creator.create_ticket()