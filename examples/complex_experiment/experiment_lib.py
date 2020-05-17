import re
import sys
from pathlib import Path

import click
from click import Choice


def _check_file(rule, input_file):
    match = re.match(rule, Path(input_file).name)
    # noinspection PyProtectedMember
    assert match, f"wrong input file {input_file} for {sys._getframe(2).f_code.co_name}"


def _check_and_generate(rule, input_file, output_file):
    _check_file(rule, input_file)
    with open(output_file, 'w+') as f:
        print(input_file, file=f)


def _check_all_and_generate(rule, input_files, output_file):
    list(map(lambda _: _check_file(rule, _), input_files))
    with open(output_file, 'w+') as f:
        print(input_files, file=f)


def encode_b(input_file, output_file):
    _check_and_generate(r"[tf]\d+", input_file, output_file)


def encode_a(input_file, output_file):
    _check_and_generate(r"[tf]\d+", input_file, output_file)


def algorithm_a(input_file, output_file):
    _check_and_generate(r"[tf]\d+.A", input_file, output_file)


def algorithm_b_build_model(input_files, output_file):
    _check_all_and_generate(r'[tf]\d+.B', input_files, output_file)


def algorithm_b(input_file, output_file, model_file):
    _check_file(r'B.model', model_file)
    _check_and_generate(r'[tf]\d+.B', input_file, output_file)


def ad_collect(input_files, output_file):
    _check_all_and_generate(r'[tf]\d+.[AB].ad', input_files, output_file)


def algorithm_c(input_file, output_file, model_file):
    _check_file(r'f.ad', model_file)
    _check_and_generate(r'[tf]\d+.A', input_file, output_file)


def algorithm_d_build_model(input_files, output_file):
    _check_all_and_generate(r'[tf]\d+.B', input_files, output_file)


def algorithm_d(input_file, output_file, model_file):
    _check_file(r'D.model', model_file)
    _check_and_generate(r'[tf]\d+.B', input_file, output_file)


def algorithm_e(input_file, output_file):
    _check_and_generate(r'[tf]\d+', input_file, output_file)


def lclz_collect(input_files, output_file):
    _check_all_and_generate(r'[tf]\d+.[CED].lclz', input_files, output_file)


@click.command()
@click.option("--mode", "-m", type=Choice(['build_model', 'run_model', 'encode', 'collect']))
@click.option(
    "--algorithm", "-a", "algorithm", default='a',
    type=Choice(['a', 'b', 'c', 'd', 'e', 'A', 'B', 'C', 'D', 'E'])
)
@click.option("--step", "-s", "step", default='ad', type=Choice(['ad', 'lclz']))
@click.option("--input", "-i", "input_file_list", multiple=True, type=str)
@click.option("--model-file", "-f", "model_file", multiple=False, type=str, default="")
@click.option("--output", "-o", "output_file", multiple=False, type=str)
def main(mode, algorithm, step, input_file_list, output_file, model_file):
    algorithm = algorithm.lower()
    if mode == "build_model":
        if algorithm == 'b':
            algorithm_b_build_model(input_file_list, output_file)
        elif algorithm == 'd':
            algorithm_d_build_model(input_file_list, output_file)
        else:
            raise RuntimeError('illegal argument')
    elif mode == 'run_model':
        if algorithm == 'a':
            algorithm_a(input_file_list[0], output_file)
        elif algorithm == 'b':
            algorithm_b(input_file_list[0], output_file, model_file)
        elif algorithm == 'c':
            algorithm_c(input_file_list[0], output_file, model_file)
        elif algorithm == 'd':
            algorithm_d(input_file_list[0], output_file, model_file)
        elif algorithm == 'e':
            algorithm_e(input_file_list[0], output_file)
        else:
            raise RuntimeError('illegal argument')
    elif mode == 'encode':
        if algorithm == 'a':
            encode_a(input_file_list[0], output_file)
        elif algorithm == 'b':
            encode_b(input_file_list[0], output_file)
        else:
            raise RuntimeError('illegal argument')
    elif mode == 'collect':
        if step == 'ad':
            ad_collect(input_file_list, output_file)
        elif step == 'lclz':
            lclz_collect(input_file_list, output_file)
        else:
            raise RuntimeError('illegal argument')
    else:
        raise RuntimeError('illegal argument')


if __name__ == '__main__':
    main()
