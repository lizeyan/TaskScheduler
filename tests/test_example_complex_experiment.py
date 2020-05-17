import os
import re
import sys
from pathlib import Path
from shlex import split

from click.testing import CliRunner

from ts import cli


def setup_ce():
    os.chdir(str(Path(__file__).parent.parent / 'examples' / 'complex_experiment'))
    sys.path.insert(0, str(Path(__file__).parent.parent))


def setup_sum():
    os.chdir(str(Path(__file__).parent.parent / 'examples' / 'sum'))
    sys.path.insert(0, str(Path(__file__).parent.parent))


def clear_output():
    _p = Path('output')
    _p.mkdir(exist_ok=True)
    for _ in _p.glob('*'):
        _.unlink()
    return _p


def test_cli_tree():
    setup_ce()
    ret = cli(args=['tree'], standalone_mode=False)


def test_cli_run():
    setup_ce()
    output = clear_output()
    cli(args=split('run -n'), standalone_mode=False)
    assert len(list(output.glob('*'))) == 0

    cli(args=['run'], standalone_mode=False)
    assert len(list(output.glob('*'))) >= 0
    assert (output / 'f.lclz').exists()
    ret_time = os.path.getmtime(str(output / 'f.lclz'))
    assert Path('.ts.history').exists()

    cli(args=['run'], standalone_mode=False)
    assert len(list(output.glob('*'))) >= 0
    assert (output / 'f.lclz').exists()
    assert ret_time == os.path.getmtime(str(output / 'f.lclz'))

    cli(args=split('run -B'), standalone_mode=False)
    assert len(list(output.glob('*'))) >= 0
    assert (output / 'f.lclz').exists()
    assert ret_time <= os.path.getmtime(str(output / 'f.lclz'))


def test_cli_sum():
    setup_sum()
    runner = CliRunner()
    ret = runner.invoke(cli, split('run -n'))
    assert ret.exit_code == 0

    ret = runner.invoke(cli, split('run'))
    assert ret.exit_code == 0
    assert re.search(r'Result: 2025', ret.output)
