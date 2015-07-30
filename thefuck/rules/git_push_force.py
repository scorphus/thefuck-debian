from thefuck import utils
from thefuck.utils import replace_argument


@utils.git_support
def match(command, settings):
    return ('push' in command.script
            and '! [rejected]' in command.stderr
            and 'failed to push some refs to' in command.stderr
            and 'Updates were rejected because the tip of your current branch is behind' in command.stderr)


@utils.git_support
def get_new_command(command, settings):
    return replace_argument(command.script, 'push', 'push --force')


enabled_by_default = False
