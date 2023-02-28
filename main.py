import inquirer
import os
import re

from termcolor import colored, cprint

from typing import Optional, List

class Settings():
    def __init__(self, sessions : Optional[str] = None, config : Optional[str] = None) -> None:
        self.HOME_DIR = os.path.expanduser('~')
        self.EXCLUDE_FILENAMES = [
            ".pub",
            "known_hosts",
            "config",
            ".kr"
        ]

        self.__sessions_directory = sessions
        self.__config_directory = config
    
    @property
    def SESSIONS_DIRECTORY(self):
        if self.__sessions_directory is None:    
            return os.path.join(self.HOME_DIR, '.ssh')
        else:
            return self.__sessions_directory
    

    @property
    def CONFIG_DIRECTORY(self):
        if self.__config_directory is None:
            return os.path.join(self.HOME_DIR, '.ssh/config')
        else:
            return self.__config_directory


SETTINGS = Settings()


def get_list_of_options(settings: Settings) -> List[str]:

    # Get a list of filenames in the folder
    files = os.listdir(SETTINGS.SESSIONS_DIRECTORY)

    # Filter out any non-files (e.g. directories)
    options = [f for f in files if os.path.isfile(os.path.join(SETTINGS.SESSIONS_DIRECTORY, f))]

    # Filter out any files that match EXCLUDE_FILENAMES
    options = [f for f in files if not any(f.endswith(ext) for ext in SETTINGS.EXCLUDE_FILENAMES)]

    return options


def replace_id_file_in_config_string(file_content: str, new_key_path: str, settings: Settings) -> str:
    # Define a regular expression to match the github.com host and its IdentityFile property
    host_pattern = r'^(Host\s+github.com\s+.*IdentityFile\s+)([^\s]+)(.*)$'

    # Construct the replacement string
    replacement = f'\\1{new_key_path}\\3'

    # Replace the IdentityFile value for the github.com host in the file content
    updated_content = re.sub(host_pattern, replacement, file_content, flags=re.I|re.M|re.S)
    return updated_content


def update_config(new_key_path: str, settings: Settings):
    # Get the current content of the config file
    with open(SETTINGS.CONFIG_DIRECTORY, "r") as ssh_config:
        config_content = ssh_config.read()

    updated_config = replace_id_file_in_config_string(config_content, new_key_path, settings)

    # Write the updated content back to the file
    with open(SETTINGS.CONFIG_DIRECTORY, 'w') as f:
        f.write(updated_config)
    
    text = colored('ID file for Host github.com in config changed successfully', 'cyan') + colored('\nConfig File: ', 'cyan') + f"({SETTINGS.CONFIG_DIRECTORY})" + colored('\nNew ID File: ', 'cyan') + f"({new_key_path})"
    print(text)
    return 

text = colored('Welcome to git-ssh session configurator', 'cyan')

print(text)

questions = [
    inquirer.List(
        name='ssh-key',
        message="Select SSH-key (session)",
        choices=get_list_of_options(SETTINGS),
    ),
]

answer = inquirer.prompt(questions)

if answer is None:
    print(colored('Ooops... Bye!', 'cyan'))
    exit(0)

new_key_path = os.path.join(SETTINGS.SESSIONS_DIRECTORY, answer['ssh-key'])

print(colored(f"You selected: {answer['ssh-key']}", 'cyan'))

update_config(new_key_path, SETTINGS)

