import tkinter as tk
from typing import List, Optional, Tuple

from pynput import keyboard
from pynput.keyboard import Key

from whichkey import WhichKeyArgs, WhichKeyHandler
from whichkey.models import IWhichKey, WhichKeyMenu


class WhichkeyUiMenu(tk.Frame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.max_columns = 10
        self.max_rows = 5
        self.frm_keys = None

    def _create_frame(self, columns: int, rows: int) -> tk.Frame:
        frame = tk.Frame(self)
        for row in range(rows):
            frame.grid_rowconfigure(row, weight=0)
        for column in range(columns):
            frame.grid_columnconfigure(column, weight=1)
        return frame

    def _column_and_rows(self, keys: List[IWhichKey]) -> Tuple[int, int]:
        max_columns = min(self.max_columns, len(keys) // self.max_rows)
        max_rows = min(self.max_rows, len(keys) // self.max_columns)
        return max_columns, max_rows

    def _key_frame(self, key: IWhichKey) -> tk.Frame:
        frm_key = tk.Frame(self.frm_keys)
        frm_key.grid_rowconfigure(0, weight=1)
        frm_key.grid_columnconfigure(0, weight=0)
        frm_key.grid_columnconfigure(1, weight=1)
        lbl_key = tk.Label(frm_key, text=key.key)
        lbl_key.grid(row=0, column=0, sticky=tk.W)
        lbl_description = tk.Label(frm_key, text=key.description)
        lbl_description.grid(row=0, column=1, sticky=tk.W)
        return frm_key

    def _get_frame(self, menu: WhichKeyMenu) -> tk.Frame:
        max_columns, max_rows = self._column_and_rows(menu.subfixes)
        frame = self._create_frame(max_columns, max_rows)
        col_idx, row_idx = 0, 0
        for entry in menu.subfixes:
            key_frame = self._key_frame(entry)
            key_frame.grid(row=row_idx, column=col_idx, sticky=tk.NSEW)
            col_idx = (col_idx + 1) % max_columns
            row_idx = (row_idx + 1) % max_rows
        return frame

    def on_update_leys(self, args: WhichKeyArgs):
        if args.which_key_menu is None or len(args.which_key_menu.subfixes) == 0:
            return
        if self.frm_keys is not None:
            self.frm_keys.destroy()
        self.frm_keys = self._get_frame(args.which_key_menu)
        self.frm_keys.grid(row=0, column=0, sticky=tk.NSEW)


class WhichkeyView(tk.Tk):
    def __init__(self, controller: "UiWhichkeyController") -> None:
        super().__init__()
        self.controller = controller

        self.overrideredirect(True)  # Entfernt Titelleiste
        self.wm_attributes("-topmost", True)  # Setzt Fenster im Vordergrund

        self.menu = WhichkeyUiMenu(self)
        self.menu.pack(expand=True)
        self.display_menu()
        self.after(3000, self.controller.cloese_whichkey)
        self.mainloop()

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


class UiWhichkeyController:
    def __init__(self, handler: WhichKeyHandler) -> None:
        super().__init__()
        self.handler = handler
        self.handler.add_show_hoock(self.toggle_display)
        self.view: Optional[WhichkeyView] = None

    def on_release(self, key: Key):
        if key == Key.esc:
            if self.view is not None:
                self.view.destroy()
            # return False  # Stoppt den Listener

    def toggle_display(self, show: bool):
        if show:
            self.display_menu()
        else:
            self.cloese_whichkey()

    def display_menu(self):
        if self.view is not None:
            return
        self.view = WhichkeyView(self)

    def cloese_whichkey(self):
        if self.view is not None:
            self.view.destroy()
            self.view = None

    def create_listener(self):
        with keyboard.Listener(
            on_press=self.handler.on_press_key,
            on_release=self.on_release,  # pyright: ignore[reportArgumentType,reportArgumentType]
        ) as listener:
            listener.join()
