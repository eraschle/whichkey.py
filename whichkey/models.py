from abc import ABC
from dataclasses import asdict, dataclass, field


@dataclass
class WhichKeyConfig:
    leader_key: str
    quit_key: str
    stop_keys: list[str]

    def is_leader(self, key: str | None) -> bool:
        return key == self.leader_key

    def is_quit(self, key: str | None) -> bool:
        return key == self.quit_key

    def is_stop(self, *keys: str) -> bool:
        return all(key in self.stop_keys for key in keys)


@dataclass(frozen=True, order=True)
class WhichKey(ABC):
    key: str = field(repr=True, compare=True)
    description: str = field(repr=True, compare=False)

    def as_dict(self):
        return asdict(self)


@dataclass(frozen=True, order=True, kw_only=True)
class WhichKeyCommand(WhichKey):
    command: str = field(repr=False, compare=False)

    def execute(self):
        print(f"Execute command: {self.command}")


@dataclass(frozen=True, order=True)
class WhichKeyMenu(WhichKey):
    entries: dict[str, WhichKey] = field(default_factory=dict)

    def which_key_by(self, key: str | None) -> WhichKey:
        if key is None:
            raise ValueError("Key is None")
        which_key = self.entries.get(key, None)
        if which_key is None:
            raise ValueError(f"Key {key} not found in menu")
        return which_key

    def add_key(self, prefix: tuple[str, ...], which_key: WhichKey):
        if len(prefix) > 0:
            current_key = prefix[0]
            subfix = self.which_key_by(current_key)
            if subfix is None:
                subfix = WhichKeyMenu(key=current_key, description="Prefix")
            if not isinstance(subfix, WhichKeyMenu):
                raise ValueError(f"Key {current_key} is not a menu")
            subfix.add_key(prefix[1:], which_key)
        else:
            self.entries[which_key.key] = which_key
