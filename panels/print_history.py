import datetime
import logging
import threading

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Pango
from ks_includes.screen_panel import ScreenPanel


class Panel(ScreenPanel):
    def __init__(self, screen, title):
        title = title or _("Print History")
        super().__init__(screen, title)
        self.jobs = []

        self.buttons = {
            "refresh": self._gtk.Button(
                image_name="refresh",
                label=_("Refresh"),
                style="color3",
                scale=self.bts,
                position=Gtk.PositionType.LEFT,
                lines=1,
            ),
        }
        self.buttons["refresh"].connect("clicked", self.refresh_history)
        self.buttons["refresh"].set_vexpand(False)

        top_box = Gtk.Box(vexpand=False)
        top_box.pack_start(self.buttons["refresh"], True, True, 0)

        self.labels["no_history"] = Gtk.Label(
            label=_("No print history available"), vexpand=True
        )

        self.scroll = self._gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.add(self.labels["no_history"])

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, vexpand=True)
        main_box.pack_start(top_box, False, False, 0)
        main_box.pack_start(self.scroll, True, True, 0)

        self.content.add(main_box)

    def activate(self):
        self.refresh_history()

    def refresh_history(self, widget=None):
        self.clear_scroll()
        self.scroll.add(Gtk.Label(label=_("Loading..."), vexpand=True))
        self.scroll.show_all()
        self._gtk.Button_busy(self.buttons["refresh"], True)
        threading.Thread(target=self.fetch_history, daemon=True).start()

    def fetch_history(self):
        try:
            result = self._screen.apiclient.send_request(
                "server/history/list?limit=50&order=desc"
            )
        except Exception as e:
            logging.exception(e)
            result = None
        GLib.idle_add(self.display_history, result)

    def display_history(self, result):
        self._gtk.Button_busy(self.buttons["refresh"], False)
        self.clear_scroll()

        if not result or "jobs" not in result:
            self.scroll.add(
                Gtk.Label(label=_("Failed to load print history"), vexpand=True)
            )
            self.scroll.show_all()
            return False

        self.jobs = result["jobs"]
        if not self.jobs:
            self.scroll.add(self.labels["no_history"])
            self.scroll.show_all()
            return False

        self.scroll.add(self.build_history_grid())
        self.scroll.show_all()
        return False

    def clear_scroll(self):
        for child in self.scroll.get_children():
            self.scroll.remove(child)

    def build_history_grid(self):
        grid = Gtk.Grid(column_spacing=10, row_spacing=5)

        for i, job in enumerate(self.jobs):
            row = self.build_job_row(job)
            grid.attach(row, 0, i * 2, 1, 1)
            grid.attach(Gtk.Separator(hexpand=True), 0, i * 2 + 1, 1, 1)

        return grid

    def build_job_row(self, job):
        row = Gtk.Box(spacing=10, hexpand=True, vexpand=False)
        row.get_style_context().add_class("frame-item")

        info_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=2,
            hexpand=True,
            valign=Gtk.Align.CENTER,
        )

        # Filename
        filename = job.get("filename", _("Unknown"))
        name_label = Gtk.Label(
            halign=Gtk.Align.START,
            hexpand=True,
            ellipsize=Pango.EllipsizeMode.END,
        )
        name_label.set_markup(f"<big><b>{GLib.markup_escape_text(filename)}</b></big>")
        info_box.add(name_label)

        # Details line: status, duration, filament, date
        details = []

        status = job.get("status", "unknown")
        status_text = self.format_status(status)
        details.append(status_text)

        print_duration = job.get("print_duration")
        if print_duration and print_duration > 0:
            details.append(self.format_time(print_duration))

        filament_used = job.get("filament_used", 0)
        if filament_used and filament_used > 0:
            meters = filament_used / 1000
            details.append(f"{meters:.1f}m")

        start_time = job.get("start_time")
        if start_time:
            try:
                dt = datetime.datetime.fromtimestamp(start_time)
                details.append(dt.strftime("%Y-%m-%d %H:%M"))
            except (ValueError, OSError):
                pass

        detail_label = Gtk.Label(
            label="  |  ".join(details),
            halign=Gtk.Align.START,
            hexpand=True,
            ellipsize=Pango.EllipsizeMode.END,
        )
        info_box.add(detail_label)

        row.add(info_box)
        return row

    @staticmethod
    def format_status(status):
        status_map = {
            "completed": _("Completed"),
            "cancelled": _("Cancelled"),
            "error": _("Error"),
            "in_progress": _("In Progress"),
        }
        return status_map.get(status, status.replace("_", " ").title())

    def process_update(self, action, data):
        pass
