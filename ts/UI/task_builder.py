from collections import defaultdict, OrderedDict
from functools import reduce, partial
from itertools import product
from pathlib import Path
from typing import Union, Callable, Iterable, Tuple, List, Dict

from jinja2 import Template
from loguru import logger

from ..tasks import Task, ShellTask, CallableTask, ReadFileTask, GenerateFileTask

_task_builder_global_tasks = set()  # type: Set[Task]
_task_target_file_dict = {}  # type: Dict[Path, Task]
_task_dependency_file_dict = defaultdict(list)  # type: Dict[Task, List[Path]]

_drop_if_not_used = set()

reserved_keywords = [
    '__dependency__', '__d',
    '__target__', '__t',
]


def __if_func_accept_kwargs(func):
    import inspect
    x = inspect.signature(func)
    return any(_.kind == inspect.Parameter.VAR_KEYWORD for _ in x.parameters.values())


def _render(
        _original: Union[None, str, Path, Task, Iterable[Union[str, Path, Task]]],
        _params
) -> Union[None, str, Path, Task, Iterable[Union[str, Path, Task]]]:
    """
    render _original
    if _original is None, return None
    if _original is a list, return a list, otherwise return a str
    :param _original:
    :param _params:
    :return:
    """
    if _original is None:
        return _original
    _is_list = True
    if isinstance(_original, (Task, str, Path)):
        _original = [_original]
        _is_list = False
    _ret = []
    for _item in _original:
        if isinstance(_item, str):
            _ret.append(Template(_item).render(
                **_params
            ))
        elif isinstance(_item, Path):
            _ret.append(Path(Template(str(_item)).render(
                **_params
            )))
        else:
            _ret.append(_item)
    if _is_list:
        return _ret
    else:
        return _ret[0]


def task(
        runner: Union[str, Callable], name: str = None,
        depend: Union[Iterable[Union[Path, str, Task]], Path, str, Task] = None,
        target: Union[Iterable[Union[str, Path]], Path, str, Task] = None,
        **template_kwargs,
) -> Task:
    depend_files, depend_tasks, is_depend_list = __parse_depend(
        _render(depend, template_kwargs)
    )
    target_files, is_target_list = __parse_targets(
        _render(target, template_kwargs)
    )
    __d = list(map(str, depend_files))
    __t = list(map(str, target_files))
    if not is_depend_list:
        __d = __d[0] if len(__d) > 0 else None
    if not is_target_list:
        __t = __t[0] if len(__t) > 0 else None

    template_kwargs.update(
        __dependency__=__d, __d=__d,
        __target__=__t, __t=__t,
    )

    if isinstance(runner, str):
        ret = ShellTask(
            command=_render(runner, template_kwargs),
            name=_render(name, template_kwargs),
            dependencies=depend_tasks
        )
    elif callable(runner):
        ret = CallableTask(
            function=runner if not __if_func_accept_kwargs(runner) else partial(runner, **template_kwargs),
            name=_render(name, template_kwargs),
            dependencies=depend_tasks
        )
    else:
        raise RuntimeError(f"runner should be a bash command or python Callable: {runner}")
    _task_dependency_file_dict[ret] = depend_files
    for _ in target_files:
        _task_target_file_dict[_] = ret
    logger.debug(f"parsed Task {ret}")
    _task_builder_global_tasks.add(ret)
    return ret


def task_product(
        runner: Union[str, Callable], name: str = None,
        depend: Iterable[Union[Path, str, Task]] = None,
        target: Iterable[Union[str, Path]] = None,
        keep=False,
        **kwargs
) -> List[Task]:
    kwargs = OrderedDict(kwargs)
    keys = list(kwargs.keys())
    values_list = list(kwargs.values())
    ret = []
    for values in product(*values_list):
        params = {k: v for k, v in zip(keys, values)}
        ret.append(task(
            runner=runner,
            name=name,
            depend=depend,
            target=target,
            **params
        ))
    if not keep:
        _drop_if_not_used.update(ret)
    return ret


def __parse_depend(
        depends: Union[Iterable[Union[str, Path, Task]], Path, str, Task] = None
) -> Tuple[List[Path], List[Task], bool]:
    depend_files, depend_tasks = [], []
    is_list = True
    if depends is None:
        return depend_files, depend_tasks, False
    if isinstance(depends, (Path, str, Task)):
        depends = [depends]
        is_list = False
    for depend in depends:
        if isinstance(depend, Path):
            depend_files.append(depend.relative_to('.'))
        elif isinstance(depend, Task):
            depend_tasks.append(depend)
        elif isinstance(depend, str):
            _task_resolved = Task.task(depend)
            if _task_resolved is not None:
                depend_tasks.append(_task_resolved)
            else:
                depend_files.append(Path(depend).relative_to('.'))
        else:
            raise RuntimeError(f"wired depend type: {depend} {type(depend)}")

    return depend_files, depend_tasks, is_list


def __parse_targets(
        targets: Union[Iterable[Union[str, Path]], str, Path] = None
) -> Tuple[List[Path], bool]:
    is_list = True
    if targets is None:
        return [], False
    if isinstance(targets, (str, Path)):
        targets = [targets]
        is_list = False
    ret = []
    for target in targets:
        if isinstance(target, Path):
            ret.append(target.relative_to('.'))
        elif isinstance(target, str):
            ret.append(Path(target).relative_to('.'))
        else:
            raise RuntimeError(f"wired target type: {target} {type(target)}")
    return ret, is_list


def _file_dependency_resolved_tasks(_tasks):
    _file_tasks = set()
    _replaced = {}
    for t in _tasks:
        dependencies_files = _task_dependency_file_dict.get(t, [])
        for f in dependencies_files:
            if f in _task_target_file_dict:
                g_task = GenerateFileTask(f, _task_target_file_dict[f])
                _file_tasks.add(g_task)
                _replaced[_task_target_file_dict[f]] = g_task
                f_task = ReadFileTask(f, [g_task])
            else:
                f_task = ReadFileTask(f)
            _file_tasks.add(f_task)
            if t in _replaced:
                _replaced[t].add_dependency(f_task)
            t.add_dependency(f_task)
    return (_tasks | _file_tasks) - set(_replaced.keys())


def _remove_unused_tasks(_tasks):
    used = reduce(
        lambda a, b: a | b,
        [_.dependencies for _ in _tasks],
        set()
    )
    return _tasks - (_drop_if_not_used - used)


def _all_built_tasks():
    tasks = _task_builder_global_tasks
    tasks = _file_dependency_resolved_tasks(tasks)
    tasks = _remove_unused_tasks(tasks)
    return tasks
