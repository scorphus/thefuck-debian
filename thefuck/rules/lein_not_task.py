import re
from thefuck.utils import sudo_support, replace_argument


@sudo_support
def match(command, settings):
    return (command.script.startswith('lein')
            and "is not a task. See 'lein help'" in command.stderr
            and 'Did you mean this?' in command.stderr)


@sudo_support
def get_new_command(command, settings):
    broken_cmd = re.findall(r"'([^']*)' is not a task",
                            command.stderr)[0]
    new_cmd = re.findall(r'Did you mean this\?\n\s*([^\n]*)',
                         command.stderr)[0]
    return replace_argument(command.script, broken_cmd, new_cmd)
