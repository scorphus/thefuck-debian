# -*- encoding: utf-8 -*-

import pytest
from itertools import islice
from thefuck import ui
from thefuck.types import CorrectedCommand


@pytest.fixture
def patch_getch(monkeypatch):
    def patch(vals):
        def getch():
            for val in vals:
                if val == KeyboardInterrupt:
                    raise val
                else:
                    yield val

        getch_gen = getch()
        monkeypatch.setattr('thefuck.ui.getch', lambda: next(getch_gen))

    return patch


def test_read_actions(patch_getch):
    patch_getch([  # Enter:
                   '\n',
                   # Enter:
                   '\r',
                   # Ignored:
                   'x', 'y',
                   # Up:
                   '\x1b', '[', 'A',
                   # Down:
                   '\x1b', '[', 'B',
                   # Ctrl+C:
                   KeyboardInterrupt], )
    assert list(islice(ui.read_actions(), 5)) \
           == [ui.SELECT, ui.SELECT, ui.PREVIOUS, ui.NEXT, ui.ABORT]


def test_command_selector():
    selector = ui.CommandSelector(iter([1, 2, 3]))
    assert selector.value == 1
    selector.next()
    assert selector.value == 2
    selector.next()
    assert selector.value == 3
    selector.next()
    assert selector.value == 1
    selector.previous()
    assert selector.value == 3


@pytest.mark.usefixtures('no_colors')
class TestSelectCommand(object):
    @pytest.fixture
    def commands_with_side_effect(self):
        return [CorrectedCommand('ls', lambda *_: None, 100),
                CorrectedCommand('cd', lambda *_: None, 100)]

    @pytest.fixture
    def commands(self):
        return [CorrectedCommand('ls', None, 100),
                CorrectedCommand('cd', None, 100)]

    def test_without_commands(self, capsys):
        assert ui.select_command(iter([])) is None
        assert capsys.readouterr() == ('', 'No fucks given\n')

    def test_without_confirmation(self, capsys, commands, settings):
        settings.require_confirmation = False
        assert ui.select_command(iter(commands)) == commands[0]
        assert capsys.readouterr() == ('', 'ls\n')

    def test_without_confirmation_with_side_effects(
            self, capsys, commands_with_side_effect, settings):
        settings.require_confirmation = False
        assert ui.select_command(iter(commands_with_side_effect)) \
               == commands_with_side_effect[0]
        assert capsys.readouterr() == ('', 'ls (+side effect)\n')

    def test_with_confirmation(self, capsys, patch_getch, commands):
        patch_getch(['\n'])
        assert ui.select_command(iter(commands)) == commands[0]
        assert capsys.readouterr() == ('', u'\x1b[1K\rls [enter/↑/↓/ctrl+c]\n')

    def test_with_confirmation_abort(self, capsys, patch_getch, commands):
        patch_getch([KeyboardInterrupt])
        assert ui.select_command(iter(commands)) is None
        assert capsys.readouterr() == ('', u'\x1b[1K\rls [enter/↑/↓/ctrl+c]\nAborted\n')

    def test_with_confirmation_with_side_effct(self, capsys, patch_getch,
                                               commands_with_side_effect):
        patch_getch(['\n'])
        assert ui.select_command(iter(commands_with_side_effect))\
               == commands_with_side_effect[0]
        assert capsys.readouterr() == ('', u'\x1b[1K\rls (+side effect) [enter/↑/↓/ctrl+c]\n')

    def test_with_confirmation_select_second(self, capsys, patch_getch, commands):
        patch_getch(['\x1b', '[', 'B', '\n'])
        assert ui.select_command(iter(commands)) == commands[1]
        assert capsys.readouterr() == (
            '', u'\x1b[1K\rls [enter/↑/↓/ctrl+c]\x1b[1K\rcd [enter/↑/↓/ctrl+c]\n')
