import os
import sys
from pathlib import Path

import click
from loguru import logger

from .task_builder import _all_built_tasks, clear
from ..__init__ import __version__, __version_minor__
from ..project import Project
from ..tasks import Task


@click.group(invoke_without_command=True, context_settings=dict(
    ignore_unknown_options=True,
))
@click.option(
    "--file", '-f', 'ts_file', default='task.py',
    type=click.Path(dir_okay=False),
    help='The path to TS file'
)
@click.option(
    '--working-directory', '-w', "--working-directory",
    type=click.Path(file_okay=False),
    default='.',
    help='working directory'
)
@click.option("--debug", "-d", is_flag=True, default=False)
@click.option("--version", "-V", is_flag=True, default=False)
@click.pass_context
def cli(ctx, ts_file, debug, working_directory, version):
    if version:
        print(__version__, __version_minor__)
        return
    os.chdir(working_directory)
    logger.remove()
    logger.add(
        sys.stdout,
        level="INFO" if not debug else "DEBUG",
        format="[<green>{time}</green> <yellow>{level:>6}</yellow>] <white>{message}</white>"
    )
    ts_file = Path(ts_file)
    with open(str(ts_file.resolve()), 'r') as f:
        clear()
        exec(f.read())
    ctx.ensure_object(dict)
    ctx.obj['project'] = Project(
        tasks=_all_built_tasks(),
        history_path=ts_file.parent / f".{ts_file.name}.ts.history"
    )
    ctx.obj['debug'] = debug
    if ctx.invoked_subcommand is None:
        ctx.invoke(run)
    return ctx


# noinspection PyUnusedLocal
@cli.command("run")
@click.option(
    "--jobs", '-j', 'n_jobs', default=1, type=click.IntRange(min=0),
    help='The number of concurrent jobs, and set to 0 for as many as CPUs.'
)
@click.option(
    "--load-average", '-l', 'load_average', default=float('inf'), type=click.FloatRange(min=0.0),
    help='The maximum load average allowed'
)
@click.option(
    "--echo", "-n", "echo_only", is_flag=True, default=False
)
@click.option(
    "--start-over", "-B", "start_over", is_flag=True, default=False
)
@click.argument('task', nargs=-1, type=str)
@click.pass_context
def run(ctx, n_jobs: int, load_average: float, echo_only: bool, start_over: bool, task):
    project = ctx.obj['project']  # type: Project
    debug = ctx.obj['debug']  # type: bool
    if start_over:
        logger.debug("starting over")
        project.clear_history()
    if len(task) <= 0:
        tasks = list(filter(lambda _: len(project.graph.in_edges(_)) == 0, project.graph.nodes))
    elif isinstance(task, str):
        tasks = [Task.task(task)]
    else:
        tasks = list(map(Task.task, task))
    list(map(
        lambda t: project.run_task(
            t, n_jobs=n_jobs, load_average=load_average, echo_only=echo_only
        ),
        tasks
    ))


@cli.command("tree")
@click.argument('task', nargs=-1, type=str)
@click.pass_context
def tree(ctx, task):
    project = ctx.obj['project']  # type: Project
    if len(task) <= 0:
        logger.info("tree:" + os.linesep + project.graph.format_tree())
        return
    elif isinstance(task, str):
        tasks = [Task.task(task)]
    else:
        tasks = list(map(Task.task, task))
    for task in tasks:
        logger.info(f'=' * 40)
        logger.info(f'tree Task {task}')
        logger.info(os.linesep + project.graph.format_subtree(task))


if __name__ == '__main__':
    cli()
