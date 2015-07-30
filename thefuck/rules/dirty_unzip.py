import os
import zipfile


def _is_bad_zip(file):
    with zipfile.ZipFile(file, 'r') as archive:
        return len(archive.namelist()) > 1


def _zip_file(command):
    # unzip works that way:
    # unzip [-flags] file[.zip] [file(s) ...] [-x file(s) ...]
    #                ^          ^ files to unzip from the archive
    #                archive to unzip
    for c in command.script.split()[1:]:
        if not c.startswith('-'):
            if c.endswith('.zip'):
                return c
            else:
                return '{}.zip'.format(c)


def match(command, settings):
    return (command.script.startswith('unzip')
            and '-d' not in command.script
            and _is_bad_zip(_zip_file(command)))


def get_new_command(command, settings):
    return '{} -d {}'.format(command.script, _zip_file(command)[:-4])


def side_effect(command, settings):
    with zipfile.ZipFile(_zip_file(command), 'r') as archive:
        for file in archive.namelist():
            os.remove(file)


requires_output = False
