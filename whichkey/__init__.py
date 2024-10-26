from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional, Tuple

from pynput.keyboard import Key, KeyCode
from pywinauto import Application  # pyright: ignore[reportMissingImports]

from whichkey.models import IWhichKey, WhichKeyMenu


class WhichKeyArgs:
    def __init__(self, menu: Optional[WhichKeyMenu]) -> None:
        self._menu = menu
        self._app = None
        self._top = None
        self._title = None

    @property
    def app(self) -> Application:
        if self._app is None:
            self._app = Application().connect(active_only=True)
        return self._app

    @property
    def top(self) -> Application:
        if self._top is None:
            self._top = self.app.top_window()
        return self._top

    @property
    def title(self) -> str:
        if self._title is None:
            self._title = self.top.window_text()
        return self._title

    @property
    def which_key_menu(self) -> WhichKeyMenu:
        if self._menu is None:
            raise ValueError("Menu is not set")
        return self._menu


WhichKeyHook = Callable[[WhichKeyArgs], bool]
ToggleDisplay = Callable[[bool], None]


@dataclass
class WhichKeyConfig:
    leader_key: str = " "


class WhichKeyHandler:
    def __init__(self, config: WhichKeyConfig) -> None:
        self.root = WhichKeyMenu(prefix=None, key="w", description="WhichKey Root Entry")
        self.current_menu: Optional[WhichKeyMenu] = None
        self.inhibit_hook: List[WhichKeyHook] = []
        self.update_hook: List[WhichKeyHook] = []
        self.show_hook: List[ToggleDisplay] = []
        self.display_menu: bool = False
        self.config = config

    def add_inhibit_hoock(self, hook: WhichKeyHook) -> None:
        self.inhibit_hook.append(hook)

    def add_update_hoock(self, hook: WhichKeyHook) -> None:
        self.update_hook.append(hook)

    def add_show_hoock(self, hook: ToggleDisplay) -> None:
        self.show_hook.append(hook)

    def register(self, prefix: Tuple[str, ...], key: IWhichKey) -> None:
        self.root.add_key(prefix, key)

    def _run_inhibit_hook(self, env: WhichKeyArgs) -> bool:
        return all(not hook_func(env) for hook_func in self.inhibit_hook)

    def on_press_key(self, key) -> None:
        if key is None or key.char is None:
            return
        if self._run_inhibit_hook(WhichKeyArgs(self.current_menu)):
            self.current_menu = None
            self._run_show_hook(display=False)
        if self.display_menu and self.current_menu is not None:
            self.current_menu = self.current_menu.next_menu(key.char)
            if self.current_menu is None:
                self._run_show_hook(display=False)
            else:
                self._run_update_hook(WhichKeyArgs(self.current_menu))
        elif not self.display_menu and key.char == self.config.leader_key:
            self.current_menu = self.root
            self._run_update_hook(WhichKeyArgs(self.current_menu))
            self._run_show_hook(display=True)

    def _run_show_hook(self, display: bool) -> None:
        if self.display_menu == display:
            return
        self.display_menu = display
        for hook_func in self.show_hook:
            hook_func(display)

    def _run_update_hook(self, env: WhichKeyArgs) -> None:
        for hook_func in self.update_hook:
            hook_func(env)
