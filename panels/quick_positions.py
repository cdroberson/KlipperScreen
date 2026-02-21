import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango
from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel
from ks_includes.widgets.autogrid import AutoGrid


class Panel(ScreenPanel):
    def __init__(self, screen, title):
        title = title or _("Quick Positions")
        super().__init__(screen, title)
        self.positions = {}
        self.buttons = {}

        position_buttons = self._load_positions()

        if not position_buttons:
            msg = Gtk.Label(
                label=_("No positions configured.")
                + "\n\n"
                + _("Add a [quick_positions] section to your KlipperScreen.conf")
                + "\n\n"
                + _("Example:")
                + "\n[quick_positions]\nNozzle Clean: 150, 0, 50\nCenter: 150, 150, 50",
                wrap=True,
                wrap_mode=Pango.WrapMode.WORD_CHAR,
                hexpand=True,
                vexpand=True,
                halign=Gtk.Align.CENTER,
                valign=Gtk.Align.CENTER,
            )
            self.content.add(msg)
            return

        grid = AutoGrid(position_buttons, vertical=self._screen.vertical_mode)

        scroll = self._gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(grid)
        self.content.add(scroll)

    def _load_positions(self):
        config = self._config.get_config()
        if not config.has_section("quick_positions"):
            return []

        buttons = []
        for i, option in enumerate(config.options("quick_positions")):
            value = config.get("quick_positions", option)
            try:
                coords = [float(v.strip()) for v in value.split(",")]
                if len(coords) != 3:
                    raise ValueError(f"Expected 3 coordinates, got {len(coords)}")
                x, y, z = coords
            except (ValueError, TypeError) as e:
                logging.error(f"Invalid position '{option}': {value} ({e})")
                continue

            # Capitalize each word for display since config keys are lowercased
            display_name = option.title()
            self.positions[option] = {"x": x, "y": y, "z": z}

            style = f"color{1 + i % 4}"
            btn = self._gtk.Button("move", display_name, style, scale=3)
            btn.connect("clicked", self._move_to_position, option)
            self.buttons[option] = btn
            buttons.append(btn)

        return buttons

    def _move_to_position(self, widget, name):
        state = self._printer.get_stat("print_stats", "state")
        if state in ("printing", "paused"):
            self._screen.show_popup_message(_("Cannot move while printing"), level=2)
            return

        pos = self.positions[name]
        x, y, z = pos["x"], pos["y"], pos["z"]

        # Home if not already homed
        if self._printer.get_stat("toolhead", "homed_axes") != "xyz":
            self._screen._ws.klippy.gcode_script("G28")

        # Raise Z to safe height first, then move XY, then lower to target Z
        safe_z = max(z, 50)
        speed = 6000  # mm/min
        script = (
            f"{KlippyGcodes.MOVE_ABSOLUTE}\n"
            f"G0 Z{safe_z} F{speed}\n"
            f"G0 X{x} Y{y} F{speed}\n"
            f"G0 Z{z} F{speed}\n"
        )
        self._screen._ws.klippy.gcode_script(script)

    def process_update(self, action, data):
        pass
