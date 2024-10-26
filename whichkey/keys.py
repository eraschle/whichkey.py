from enum import Enum


class SpecialKey(str, Enum):
    SPACE = "space"
    ESC = "esc"


def is_special_key(key: str) -> bool:
    return any(key == special.value for special in SpecialKey)


class ModifierKey(str, Enum):
    ALT = "alt"
    CTRL = "ctrl"
    SHIFT = "shift"
    WIN = "win"


def is_modifier_key(key: str) -> bool:
    return any(key.startswith(mod.value) for mod in ModifierKey)
