import tkinter as tk

from pynput.keyboard import Key, KeyCode, Listener

from whichkey.handler import WhichKeyHandler
from whichkey.models import WhichKey, WhichKeyCommand, WhichKeyMenu


class WhichKeyMenuFrame(tk.Frame):
    max_columns = 10
    max_rows = 5
    column_per_key = 3

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.column_count = self.max_columns
        self.row_count = self.max_rows
        self.frm_keys = None

    def _create_frame(self) -> None:
        if self.frm_keys is not None:
            self.frm_keys.destroy()
        self.frm_keys = tk.Frame(self)
        self.frm_keys.grid(row=0, column=0, sticky=tk.NSEW)
        for row in range(self.row_count):
            self.frm_keys.grid_rowconfigure(row, weight=0)
        for column in range(self.column_count):
            col_idx = column * self.column_per_key
            self.frm_keys.grid_columnconfigure(col_idx, weight=0, minsize=20)
            self.frm_keys.grid_columnconfigure(col_idx + 1, weight=0, minsize=20)
            self.frm_keys.grid_columnconfigure(col_idx + 2, weight=1, minsize=100)

    def _set_column_and_rows(self, keys: list[WhichKey]) -> None:
        columns = min(self.max_columns, len(keys) // self.max_rows)
        self.column_count = max(1, columns)
        rows = min(self.max_rows, len(keys) // self.max_columns)
        self.row_count = max(1, rows)

    def _add_key_to(self, key: WhichKey, row: int, column: int) -> None:
        lbl_key = tk.Label(self.frm_keys, text=key.key, relief=tk.GROOVE)
        lbl_key.grid(row=row, column=column, sticky=tk.W)
        lbl_arrow = tk.Label(self.frm_keys, text=" -> ", anchor=tk.CENTER)
        lbl_arrow.grid(row=row, column=column + 1)
        lbl_description = tk.Label(self.frm_keys, text=key.description, relief=tk.GROOVE)
        lbl_description.grid(row=row, column=column + 2, sticky=tk.W)

    def _add_to_column(self, keys: list[WhichKey], column: int) -> None:
        for row in range(self.row_count):
            self._add_key_to(keys.pop(0), row=row, column=column)

    def _add_key_to_frame(self, keys: list[WhichKey]) -> None:
        col_idx = 0
        while len(keys) > 0:
            column = col_idx * self.column_per_key
            self._add_to_column(keys, column)
            col_idx = (col_idx + 1) % self.column_count

    def update_menu(self, menu: WhichKeyMenu | None) -> None:
        if menu is None:
            return
        keys = sorted(menu.entries.values())
        self._set_column_and_rows(keys=keys)
        self._create_frame()
        self._add_key_to_frame(keys=keys)


class WhichkeyView(tk.Tk):
    def __init__(self, menu: WhichKeyMenu) -> None:
        super().__init__()
        self.current = menu
        self.overrideredirect(True)  # Entfernt Titelleiste
        self.wm_attributes("-topmost", True)  # Setzt Fenster im Vordergrund
        for idx in range(1):
            self.grid_rowconfigure(idx, weight=idx)
            self.grid_columnconfigure(idx, weight=idx)

        self.menu = WhichKeyMenuFrame(self)
        self.menu.update_menu(self.current)
        self.menu.grid(row=0, column=0, sticky=tk.NSEW)
        self.bind("<Key>", self.on_key_press)

    def on_key_press(self, event):
        print("Tkinter key press", event.char)
        if event.char is None:
            return
        whichkey = self.current.which_key_by(event.char)
        if isinstance(whichkey, WhichKeyCommand):
            whichkey.execute()
            self.destroy()
        if isinstance(whichkey, WhichKeyMenu):
            self.current = whichkey
            self.menu.update_menu(whichkey)

    def _screen_x(self, width: float) -> int:
        screen_width = self.winfo_screenwidth()
        return int((screen_width / 2) - (width / 2))

    def _screen_y(self, height: float) -> int:
        screen_height = self.winfo_screenheight()
        return int(screen_height - (height))

    def display_menu(self, height: float = 300):
        width = self.winfo_screenwidth()
        x_center = self._screen_x(width)
        y_center = self._screen_y(height)
        geometry = f"{width}x{height}+{x_center}+{y_center}"
        self.geometry(geometry)


class WhichkeyApp:
    def __init__(self, handler: WhichKeyHandler) -> None:
        self.handler = handler
        self.handler.show_hook.add(self.on_display)
        self.view: WhichkeyView | None = None

    def on_display(self, show: bool):
        if show:
            self.display_menu()
        else:
            self.close_whichkey()

    def display_menu(self):
        if self.view is not None:
            return
        self.view = WhichkeyView(self.handler.root_menu)
        self.view.display_menu()
        self.view.after(3000, self.close_whichkey)
        self.view.mainloop()

    def close_whichkey(self):
        if self.view is not None:
            self.view.destroy()
            self.view = None

    def get_key_code(self, key) -> str | None:
        if key is None:
            return None
        if isinstance(key, KeyCode):
            return key.char
        if isinstance(key, Key):
            return key.name
        if not isinstance(key, str):
            raise ValueError(f"Not supported: {key} ({type(key)})")
        return key

    def on_press(self, key_code) -> None:
        if self.view is None and self.handler.do_inhibit_display():
            return
        key_code = self.get_key_code(key_code)
        if key_code is None:
            return
        self.handler.on_press_key(key_code)

    def stop_listening(self, key_code: str) -> bool:
        keys = self.handler.pressed_mod
        return self.handler.config.is_stop(*keys, key_code)

    def on_release(self, key) -> None:
        key_code = self.get_key_code(key)
        if key_code is None:
            return
        if self.stop_listening(key_code):
            raise Listener.StopException()
        self.handler.on_release_key(key_code)


if __name__ == "__main__":
    from whichkey import keys
    from whichkey.models import WhichKeyConfig

    config = WhichKeyConfig(
        leader_key=keys.SpecialKey.SPACE,
        quit_key=keys.SpecialKey.ESC,
        stop_keys=[keys.ModifierKey.CTRL, "c"],
    )
    handler = WhichKeyHandler(config=config)
    handler.register((), WhichKeyCommand(key="r", description="Menu A", command="echo 'Menu A'"))
    which_key = WhichkeyApp(handler=handler)
    which_key.display_menu()
