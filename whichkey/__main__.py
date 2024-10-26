from pynput import keyboard

from whichkey.handler import WhichKeyHandler
from whichkey.keys import ModifierKey, SpecialKey
from whichkey.models import WhichKeyCommand, WhichKeyConfig
from whichkey.ui import WhichkeyApp

if __name__ == "__main__":
    config = WhichKeyConfig(
        leader_key=SpecialKey.SPACE,
        quit_key=SpecialKey.ESC,
        stop_keys=[ModifierKey.CTRL, "c"],
    )
    handler = WhichKeyHandler(config=config)
    handler.register((), WhichKeyCommand(key="a", description="Menu A", command="echo 'Menu A'"))
    which_key = WhichkeyApp(handler=handler)
    with keyboard.Listener(
        on_press=which_key.on_press,
        on_release=which_key.on_release,
    ) as listener:
        listener.join()
