import json
import os
import time
from concurrent.futures.thread import ThreadPoolExecutor
from functools import reduce
from pathlib import Path
from threading import Condition
from typing import Iterable, Union, Dict, Set

from loguru import logger

from .DAG import DAG
from .tasks import Task, EmptyTask


class ProjectHistory(object):
    """
    Save a Project running status
    """

    def __init__(self, path=Path('.ts.history')):
        self._database = {}  # type: Dict[str, float]
        self._path = path

    @staticmethod
    def load(path: Path) -> 'ProjectHistory':
        """
        :param path: If path is not valid, a new ProjectHistory will be created
        :return:
        """
        try:
            with open(str(path.resolve()), 'r') as f:
                database = json.load(f)
        except FileNotFoundError:
            database = {}
        ret = ProjectHistory(path=path)
        ret._database = database
        return ret

    def save(self):
        """
        Save ProjectHistory to the given path
        :return:
        """
        with open(str(self._path.resolve()), 'w+') as f:
            json.dump(self._database, f, indent=4)
        return self

    def need_update(self, task: Union[Task, Path]) -> bool:
        """
        Whether a task need update based on the records status.
        :param task:
        :return:
        """
        if isinstance(task, Path):
            return not task.exists()
        if task.name not in self._database:
            return True
        task_time = self._database.get(task.name)
        return task.need_rerun(task_time)

    def set_status_(self, task: Task):
        """
        Set a task's status
        :param task:
        :return:
        """
        tic = time.time()
        self._database[task.name] = tic
        self.save()
        return self


class Project(object):
    """
    A structured container of tasks.
    """
    SUCCESS = 0
    FAIL = 1
    RUNNING = 2
    TODO = 3

    def __init__(self, tasks: Iterable[Task] = None, history_path: Path = Path('.ts.history')):
        """
        :param tasks: A iterable of tasks
        :param history_path: if path is not valid
        """
        self._history = ProjectHistory.load(history_path)
        self._tasks = set() if tasks is None else set(tasks)  # type: Set[Task]
        self._dependency_graph = None
        self._build_dependency_graph()

        root = EmptyTask("root", dependencies=list(filter(lambda x: len(self.graph.in_edges(x)) == 0, self.graph.nodes)))
        self._tasks.add(root)
        self._build_dependency_graph()

        self._task_finish_condition = Condition()

        self._task_status_dict = {
            task: self.TODO if self._history.need_update(task) else self.SUCCESS for task in self._tasks
        }
        self._tic_dict = {

        }

    def is_task_runnable(self, task: Task) -> bool:
        """
        A task is runnable is all its dependencies statuses are SUCCESS and its status is _TODO
        :param task:
        :return:
        """
        if any([self._task_status_dict[_] == self.FAIL for _ in task.dependencies]):
            self._task_status_dict[task] = self.FAIL
            return False
        ret = self._task_status_dict[task] == self.TODO and reduce(
            lambda a, b: a and b,
            [self._task_status_dict[_] == self.SUCCESS for _ in task.dependencies],
            True
        )
        return ret

    def find_runnable(self, todo_task_set: Set[Task]) -> Union[Task, None]:
        """
        find runnable task and remove started, failed, finished tasks
        :param todo_task_set:
        :return:
        """
        for _task in todo_task_set.copy():
            if self.is_task_runnable(_task):
                logger.debug(f"Task {_task} is runnable")
                return _task
            elif self.task_status[_task] in (self.RUNNING, self.SUCCESS, self.FAIL):
                todo_task_set.discard(_task)
        else:
            return None

    @property
    def task_status(self) -> Dict[Task, str]:
        return self._task_status_dict

    @property
    def graph(self) -> DAG:
        return self._dependency_graph

    def task_done(self, task: Task, success=True, echo_only=False):
        tic = self._tic_dict[task]
        toc = time.time()
        logger.info(f"{task} {'finished' if success else 'failed'}, elapsed time: {toc - tic:.2f}s")
        self._task_finish_condition.acquire()
        self._task_finish_condition.notify()
        self._task_finish_condition.release()
        self._task_status_dict[task] = self.SUCCESS if success else self.FAIL
        if success and not echo_only:
            self._history.set_status_(task)

    def task_started(self, task: Task):
        logger.info(f"{task} started")
        self._tic_dict[task] = time.time()
        self._task_status_dict[task] = self.RUNNING

    @property
    def tasks(self):
        return self._tasks

    def _build_dependency_graph(self):
        nodes = self._tasks
        edges = reduce(
            lambda a, b: a | b,
            [set((task, d_task) for d_task in task.dependencies) for task in self._tasks],
            set()
        )
        self._dependency_graph = DAG(nodes, edges)
        return self

    def run_task(self, task: Task, n_jobs: int, load_average: float, echo_only: bool):
        if self.task_status.get(task, None) == 'FINISHED':
            logger.debug(f"Task {task} finished already")
            return
        logger.info(f"Run Task {task} with {n_jobs} jobs, {load_average} load average")
        todo_task_set = self._dependency_graph.dependency_subgraph(task).nodes  # type: Set[Task]

        def get_job(_task: Task):
            if echo_only:
                return lambda _=_task: logger.info((str(_)))
            else:
                return lambda _=_task: _()

        if echo_only:
            def callback(_future):
                _task = future_to_task[_future]
                self.task_done(_task, echo_only=True)
        else:
            def callback(_future):
                _task = future_to_task[_future]
                _status, _ret = _future.result()
                self.task_done(_task, success=_status, echo_only=False)
                if not _status:
                    logger.error(f"Error occurs in Task {_task!s}: {_ret}")

        future_to_task = {}
        with ThreadPoolExecutor(max_workers=n_jobs if n_jobs > 0 else None) as pool:
            while len(todo_task_set) > 0:
                task = self.find_runnable(todo_task_set)
                if len(todo_task_set) <= 0:
                    break
                elif task is None:
                    self._task_finish_condition.acquire()
                    self._task_finish_condition.wait()
                    self._task_finish_condition.release()
                    continue
                while os.getloadavg()[0] > load_average:
                    time.sleep(0.5)
                self.task_started(task)
                future = pool.submit(get_job(task))
                future_to_task[future] = task
                future.add_done_callback(callback)

    def clear_history(self):
        self._history = ProjectHistory()
        self._task_status_dict = {
            task: self.TODO if self._history.need_update(task) else self.SUCCESS for task in self._tasks
        }
        return self
