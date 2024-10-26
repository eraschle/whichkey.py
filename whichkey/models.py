from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import List, Optional, Protocol, Tuple, TypeGuard

from pynput.keyboard import KeyCode


class IWhichKey(Protocol):
    prefix: Optional["IWhichKey"]
    key: str
    description: str

    @property
    def keys(self) -> List[str]: ...

    def __eq__(self, value: object, /) -> bool: ...

    def __lt__(self, value: object, /) -> bool: ...


@dataclass(frozen=True, order=True)
class AWhichKeyCommand(ABC, IWhichKey):
    prefix: Optional[IWhichKey]
    key: str = field(repr=True, compare=True)
    description: str = field(repr=True, compare=False)

    @property
    def keys(self) -> List[str]:
        if self.prefix is None:
            return [self.key]
        return self.prefix.keys + [self.key]

    def as_dict(self):
        return asdict(self)


@dataclass(frozen=True, order=True)
class WhichKeyCommand(AWhichKeyCommand):
    command: str = field(repr=False, compare=False)

    def execute(self):
        pass


@dataclass(frozen=True, order=True)
class WhichKeyMenu(AWhichKeyCommand):
    subfixes: List[IWhichKey] = field(default_factory=list)

    def is_menu(self, key: str, which_key: IWhichKey) -> TypeGuard["WhichKeyMenu"]:
        if key != which_key.key:
            return False
        return isinstance(which_key, WhichKeyMenu)

    def next_menu(self, key: Optional[str]) -> Optional["WhichKeyMenu"]:
        if key is None:
            return None
        for subkey in self.subfixes:
            if self.is_menu(key, subkey):
                return subkey
        return None

    def _get_or_create(
        self, key: str, keys: List[IWhichKey], prefix: Optional[IWhichKey] = None
    ) -> IWhichKey:
        entires = [elem for elem in keys if elem.key == key]
        if len(entires) > 1:
            raise ValueError("Expected zero or one key")
        if len(entires) == 0:
            return WhichKeyMenu(prefix, key, "Prefix")
        return entires[0]

    def add_key(self, prefix: Tuple[str, ...], key: IWhichKey):
        if len(prefix) == 0:
            self.subfixes.append(key)
            self.subfixes.sort()
        else:
            subfix = self._get_or_create(prefix[0], self.subfixes, self)
            if not isinstance(subfix, WhichKeyMenu):
                raise ValueError("Expected a whichkey menu")
            subfix.add_key(prefix[1:], key)
