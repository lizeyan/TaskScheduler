"""
Task Scheduler module
"""
from subprocess import getoutput

from .UI import *
from .tasks import Task, ShellTask, CallableTask
from .utility import str_product

__all__ = [
    "task", "task_product",
    "Task", "ShellTask", "CallableTask",
    "str_product",
    "cli",
    "import_tasks",
]

__version__ = f'0.0.1.2'
__version_minor__ = f'{getoutput("git rev-parse HEAD")[:10]}@{getoutput("git rev-parse --abbrev-ref HEAD")}'
