from whichkey import keys
from whichkey.events import WhichKeyHook, WhichKeyInhibitArgs
from whichkey.models import WhichKey, WhichKeyConfig, WhichKeyMenu


class WhichKeyHandler:
    def __init__(self, config: WhichKeyConfig) -> None:
        self.config = config
        self.root_menu = WhichKeyMenu(key="", description="Root menu")
        self.inhibit_hook = WhichKeyHook[WhichKeyInhibitArgs, bool]()
        self.show_hook = WhichKeyHook[bool, None]()
        self.pressed_mod = set()

    def register(self, prefix: tuple[str, ...], key: WhichKey) -> None:
        self.root_menu.add_key(prefix, key)

    def do_inhibit_display(self) -> bool:
        if not self.inhibit_hook:
            return False
        args = WhichKeyInhibitArgs()
        return all(not func(args) for func in self.inhibit_hook)

    def on_press_key(self, key_code: str) -> None:
        if keys.is_modifier_key(key_code):
            self.pressed_mod.add(key_code)
        if self.config.is_leader(key_code):
            # Leader key pressed > show which key menu
            self.show_hook(args=True)
        elif self.config.is_quit(key_code):
            # Quit key pressed > close which key menu
            self.show_hook(args=False)

    def on_release_key(self, key_code: str) -> None:
        if not keys.is_modifier_key(key_code):
            return
        self.pressed_mod.discard(key_code)
