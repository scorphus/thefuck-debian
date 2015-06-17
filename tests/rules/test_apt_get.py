import pytest
from mock import Mock, patch
from thefuck.rules import apt_get
from thefuck.rules.apt_get import match, get_new_command
from tests.utils import Command


# python-commandnotfound is available in ubuntu 14.04+
@pytest.mark.skipif(not getattr(apt_get, 'enabled_by_default', True),
                    reason='Skip if python-commandnotfound is not available')
@pytest.mark.parametrize('command', [
    Command(script='vim', stderr='vim: command not found')])
def test_match(command):
    assert match(command, None)


@pytest.mark.parametrize('command, return_value', [
    (Command(script='vim', stderr='vim: command not found'),
     [('vim', 'main'), ('vim-tiny', 'main')])])
@patch('thefuck.rules.apt_get.CommandNotFound', create=True)
@patch.multiple(apt_get, create=True, apt_get='apt_get')
def test_match_mocked(cmdnf_mock, command, return_value):
    get_packages = Mock(return_value=return_value)
    cmdnf_mock.CommandNotFound.return_value = Mock(getPackages=get_packages)
    assert match(command, None)
    assert cmdnf_mock.CommandNotFound.called
    assert get_packages.called


@pytest.mark.parametrize('command', [
    Command(script='vim', stderr=''), Command()])
def test_not_match(command):
    assert not match(command, None)


# python-commandnotfound is available in ubuntu 14.04+
@pytest.mark.skipif(not getattr(apt_get, 'enabled_by_default', True),
                    reason='Skip if python-commandnotfound is not available')
@pytest.mark.parametrize('command, new_command', [
    (Command('vim'), 'sudo apt-get install vim && vim'),
    (Command('convert'), 'sudo apt-get install imagemagick && convert')])
def test_get_new_command(command, new_command):
    assert get_new_command(command, None) == new_command


@pytest.mark.parametrize('command, new_command, return_value', [
    (Command('vim'), 'sudo apt-get install vim && vim',
     [('vim', 'main'), ('vim-tiny', 'main')]),
    (Command('convert'), 'sudo apt-get install imagemagick && convert',
     [('imagemagick', 'main'),
      ('graphicsmagick-imagemagick-compat', 'universe')])])
@patch('thefuck.rules.apt_get.CommandNotFound', create=True)
@patch.multiple(apt_get, create=True, apt_get='apt_get')
def test_get_new_command_mocked(cmdnf_mock, command, new_command, return_value):
    get_packages = Mock(return_value=return_value)
    cmdnf_mock.CommandNotFound.return_value = Mock(getPackages=get_packages)
    assert get_new_command(command, None) == new_command
    assert cmdnf_mock.CommandNotFound.called
    assert get_packages.called
