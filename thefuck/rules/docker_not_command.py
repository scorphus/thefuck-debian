from itertools import dropwhile, takewhile, islice
import re
import subprocess
from thefuck.utils import get_closest, sudo_support, replace_argument


@sudo_support
def match(command, settings):
    return command.script.startswith('docker') \
           and 'is not a docker command' in command.stderr


def get_docker_commands():
    proc = subprocess.Popen('docker', stdout=subprocess.PIPE)
    lines = [line.decode('utf-8') for line in proc.stdout.readlines()]
    lines = dropwhile(lambda line: not line.startswith('Commands:'), lines)
    lines = islice(lines, 1, None)
    lines = list(takewhile(lambda line: line != '\n', lines))
    return [line.strip().split(' ')[0] for line in lines]


@sudo_support
def get_new_command(command, settings):
    wrong_command = re.findall(
        r"docker: '(\w+)' is not a docker command.", command.stderr)[0]
    fixed_command = get_closest(wrong_command, get_docker_commands())
    return replace_argument(command.script, wrong_command, fixed_command)
