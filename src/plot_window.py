import gettext

import gi
gi.require_version('Adw', '1')
gi.require_version('Gdk', '4.0')
gi.require_version('Gtk', '4.0')

from gi.repository import Adw, Gdk, GLib, Gtk
from html import escape

_ = gettext.gettext


class TaunoPlotWindow(Adw.ApplicationWindow):
    def __init__(self, parent, plot_data):
        super().__init__(
            application=parent.get_application(),
            transient_for=parent,
            title=_("Live Plot"),
            default_width=800,
            default_height=500,
        )

        self.plot_data = plot_data
        self._refresh_pending = False
        self._refresh_source_id = GLib.timeout_add(33, self.refresh_pending)

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label=_("Live Plot")))

        clear_button = Gtk.Button.new_from_icon_name("edit-clear-symbolic")
        clear_button.set_tooltip_text(_("Clear plot"))
        clear_button.connect("clicked", self.on_clear_clicked)
        header.pack_end(clear_button)
        root.append(header)

        self.picture = Gtk.Picture()
        self.picture.set_content_fit(Gtk.ContentFit.CONTAIN)
        self.picture.set_hexpand(True)
        self.picture.set_vexpand(True)
        self.picture.set_margin_start(12)
        self.picture.set_margin_end(12)
        self.picture.set_margin_top(12)
        self.picture.set_accessible_role(Gtk.AccessibleRole.IMG)
        self.picture.update_property(
            [Gtk.AccessibleProperty.LABEL], [_("Live serial plot")]
        )

        value_label = Gtk.Label(label=_("Value"))
        value_label.set_halign(Gtk.Align.CENTER)
        root.append(value_label)
        root.append(self.picture)

        sample_label = Gtk.Label(label=_("Sample"))
        sample_label.set_halign(Gtk.Align.CENTER)
        root.append(sample_label)

        self.legend_label = Gtk.Label(xalign=0)
        self.legend_label.set_use_markup(True)
        self.legend_label.set_wrap(True)
        self.legend_label.set_margin_start(12)
        self.legend_label.set_margin_end(12)
        root.append(self.legend_label)

        self.status_label = Gtk.Label(xalign=1)
        self.status_label.set_margin_start(12)
        self.status_label.set_margin_end(12)
        self.status_label.set_margin_top(6)
        self.status_label.set_margin_bottom(12)
        root.append(self.status_label)

        self.set_content(root)
        self.connect("close-request", self.on_close_request)
        self.refresh()

    def on_clear_clicked(self, button):
        self.plot_data.clear()
        self.refresh()

    def on_close_request(self, window):
        if self._refresh_source_id is not None:
            GLib.source_remove(self._refresh_source_id)
            self._refresh_source_id = None
        return False

    def queue_refresh(self):
        self._refresh_pending = True

    def refresh_pending(self):
        if self._refresh_pending:
            self._refresh_pending = False
            self.refresh()
        return True

    def refresh(self):
        series = self.plot_data.series
        series_count = len(series)
        sample_count = sum(len(values) for values in series.values())
        self.status_label.set_text(
            _("Series: {series} · Samples: {samples}").format(
                series=series_count, samples=sample_count
            )
        )
        colors = self._series_colors()
        legend = [
            f'<span foreground="{colors[index]}">■</span> {escape(label)}'
            for index, label in enumerate(series)
        ]
        self.legend_label.set_markup("    ".join(legend))
        self.picture.set_paintable(self.render_texture())

    @staticmethod
    def _draw_line(pixels, width, height, x1, y1, x2, y2, color, thickness=1):
        dx = abs(x2 - x1)
        sx = 1 if x1 < x2 else -1
        dy = -abs(y2 - y1)
        sy = 1 if y1 < y2 else -1
        error = dx + dy

        while True:
            radius = thickness // 2
            for y in range(max(0, y1 - radius), min(height, y1 + radius + 1)):
                for x in range(max(0, x1 - radius), min(width, x1 + radius + 1)):
                    offset = (y * width + x) * 4
                    pixels[offset:offset + 4] = color
            if x1 == x2 and y1 == y2:
                break
            doubled_error = 2 * error
            if doubled_error >= dy:
                error += dy
                x1 += sx
            if doubled_error <= dx:
                error += dx
                y1 += sy

    def render_texture(self):
        width, height = 960, 500
        pixels = bytearray(width * height * 4)
        series = [
            list(values)
            for values in self.plot_data.series.values()
            if values
        ]
        left, right, top, bottom = 72, 20, 20, 52
        plot_width = max(1, width - left - right)
        plot_height = max(1, height - top - bottom)
        foreground = self.get_style_context().get_color()
        grid_color = (
            round(foreground.red * 255),
            round(foreground.green * 255),
            round(foreground.blue * 255),
            52,
        )
        axis_color = (*grid_color[:3], 150)
        series_colors = self._series_colors()

        for tick in range(5):
            y = top + plot_height * tick // 4
            self._draw_line(
                pixels, width, height, left, y, width - right, y, grid_color
            )
        self._draw_line(
            pixels, width, height, left, top, left, top + plot_height, axis_color
        )
        self._draw_line(
            pixels, width, height, left, top + plot_height,
            width - right, top + plot_height, axis_color
        )

        flat_values = [value for values in series for value in values]
        if flat_values:
            value_scale = max(1.0, abs(min(flat_values)), abs(max(flat_values)))
            scaled_series = [
                [value / value_scale for value in values] for values in series
            ]
            all_scaled_values = [
                value for values in scaled_series for value in values
            ]
            minimum = min(all_scaled_values)
            maximum = max(all_scaled_values)
            value_range = maximum - minimum
            padding = (
                value_range * 0.05
                if value_range
                else max(0.05, abs(maximum) * 0.05)
            )
            minimum -= padding
            maximum += padding

            for series_index, values in enumerate(scaled_series):
                points = []
                for index, value in enumerate(values):
                    x = left + plot_width * index // max(1, len(values) - 1)
                    y = top + round(
                        plot_height * (maximum - value) / (maximum - minimum)
                    )
                    points.append((x, y))

                line_color = self._rgb_color(series_colors[series_index])
                if len(points) == 1:
                    self._draw_line(
                        pixels,
                        width,
                        height,
                        *points[0],
                        *points[0],
                        line_color,
                        5,
                    )
                else:
                    for start, end in zip(points, points[1:]):
                        self._draw_line(
                            pixels, width, height, *start, *end, line_color, 2
                        )

        texture_data = GLib.Bytes.new(pixels)
        return Gdk.MemoryTexture.new(
            width,
            height,
            Gdk.MemoryFormat.R8G8B8A8,
            texture_data,
            width * 4,
        )

    @staticmethod
    def _series_colors():
        return (
            "#3584e4",
            "#e66100",
            "#33d17a",
            "#c061cb",
            "#f6d32d",
            "#ff7800",
            "#62a0ea",
            "#ed333b",
            "#26a269",
            "#9141ac",
            "#1c71d8",
            "#a51d2d",
            "#865e3c",
            "#5e5c64",
            "#c64600",
            "#1a5fb4",
        )

    @staticmethod
    def _rgb_color(color):
        return tuple(int(color[index:index + 2], 16) for index in (1, 3, 5)) + (255,)
