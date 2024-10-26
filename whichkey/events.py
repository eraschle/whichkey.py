from typing import Callable, List

from pywinauto import Application, WindowSpecification


class WhichKeyInhibitArgs:
    def __init__(self) -> None:
        self._app = None
        self._top = None
        self._title = None

    @property
    def app(self) -> Application:
        if self._app is None:
            self._app = Application().connect(active_only=True)
        return self._app

    @property
    def top(self) -> WindowSpecification:
        if self._top is None:
            self._top = self.app.top_window()
        return self._top

    @property
    def title(self) -> str:
        if self._title is None:
            self._title = self.top.window_text()
        return self._title


class WhichKeyHook[TArgs, TReturn]:
    def __init__(self) -> None:
        self._hooks: List[Callable[[TArgs], TReturn]] = []

    def add(self, func: Callable[[TArgs], TReturn]) -> None:
        self._hooks.append(func)

    def clear(self) -> None:
        self._hooks.clear()

    def __bool__(self) -> bool:
        return len(self._hooks) > 0

    def __iter__(self):
        return iter(self._hooks)

    def __call__(self, args: TArgs) -> None:
        for func in self:
            func(args)
