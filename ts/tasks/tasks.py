import os
from pathlib import Path
from subprocess import Popen
from typing import Iterable, Callable, Tuple, Any, Set


class Task(object):
    __name_to_instance = {}

    @staticmethod
    def clear():
        Task.__name_to_instance = {}

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        if instance.name in cls.__name_to_instance:
            return cls.__name_to_instance[instance.name]
        else:
            cls.__name_to_instance[instance.name] = instance
            return instance

    def __init__(
            self, name, *,
            dependencies: "Iterable[Task]" = None,
    ):
        """
        :param dependencies:
        """
        if hasattr(self, '__initialized'):
            return
        self.__initialized = True
        self._name = name
        self._children = set(dependencies) if dependencies is not None else set()  # type: Set[Task]
        self._result = None

    @staticmethod
    def task(name: str):
        return Task.__name_to_instance.get(name, None)

    @property
    def result(self) -> Any:
        return self._result

    @property
    def name(self) -> str:
        return self._name

    @property
    def dependencies(self) -> 'Set[Task]':
        return self._children

    def add_dependency(self, task: "Task"):
        self.dependencies.add(task)

    def __call__(self, *args, **kwargs) -> Tuple[bool, Any]:
        raise NotImplementedError()

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def need_rerun(self, time: float = None) -> bool:
        if time is None:
            return True
        return any(
            _.need_rerun(time) for _ in self.dependencies
        )

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return id(self)


class EmptyTask(Task):
    def __call__(self, *args, **kwargs) -> Tuple[bool, Any]:
        return True, None


class ShellTask(Task):
    def __str__(self):
        return self.__str

    def __init__(
            self, command: str, name: str = None,
            dependencies: Iterable[Task] = None,
    ):
        self.__str = f"{name}" if name is not None else f"\"{command}\""
        if name is None:
            name = command
        super().__init__(
            name=name, dependencies=dependencies
        )
        self.__command = command

    def __call__(self, *args, **kwargs):
        job = Popen(self.__command, shell=True)
        try:
            ret = job.wait()
        except KeyboardInterrupt:
            job.terminate()
            return False, None
        self._result = ret
        return ret == 0, ret


class CallableTask(Task):
    def __str__(self):
        return self.name

    def need_rerun(self, time: float = None) -> bool:
        return True

    def __init__(
            self, function: Callable, name: str = None,
            dependencies: Iterable[Task] = None,
    ):
        if name is None:
            if hasattr(function, '__name__'):
                name = function.__name__
            elif hasattr(function, '__class__'):
                name = function.__class__
            else:
                name = repr(function)
        super().__init__(
            name=name, dependencies=dependencies
        )
        self.__function = function

    def __call__(self, *args, **kwargs):
        try:
            self._result = self.__function(*[_.result for _ in self.dependencies], *args, **kwargs)
        except Exception as e:
            return False, e
        else:
            return True, self.result


class GenerateFileTask(Task):
    def __call__(self, *args, **kwargs) -> Tuple[bool, Any]:
        self._result = self.base()
        return self._result

    def __str__(self):
        return f"Generate {self.path}<-{self.base}"

    def __init__(self, path: Path, base: Task):
        """
        :param path: path to the file
        :param base: based on this task to generate the file
        """
        super().__init__(
            name=f"{str(path.relative_to('.'))}<-{base.name}",
            dependencies=base.dependencies
        )
        self.path = path
        self.base = base

    def need_rerun(self, time: float = None) -> bool:
        return (not self.path.exists()) or super().need_rerun(time)


class ReadFileTask(Task):
    def __call__(self, *args, **kwargs) -> Tuple[bool, Any]:
        self._result = self.path.exists()
        return self._result, None

    def __init__(self, path: Path, dependencies: Iterable[Task] = None):
        super().__init__(
            name=f"{str(path.relative_to('.'))}",
            dependencies=dependencies
        )
        self.path = path

    def need_rerun(self, time: float = None) -> bool:
        return (not self.path.exists()) or super().need_rerun(time) or os.path.getmtime(str(self.path.resolve())) > time
