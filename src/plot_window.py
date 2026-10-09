import gettext

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')

from gi.repository import Adw, GLib, Gtk
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
        self._refresh_source_id = None

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label=_("Live Plot")))

        clear_button = Gtk.Button.new_from_icon_name("edit-clear-symbolic")
        clear_button.set_tooltip_text(_("Clear plot"))
        clear_button.connect("clicked", self.on_clear_clicked)
        header.pack_end(clear_button)
        root.append(header)

        self.plot_area = Gtk.DrawingArea()
        self.plot_area.set_hexpand(True)
        self.plot_area.set_vexpand(True)
        self.plot_area.set_margin_start(12)
        self.plot_area.set_margin_end(12)
        self.plot_area.set_margin_top(12)
        self.plot_area.set_accessible_role(Gtk.AccessibleRole.IMG)
        self.plot_area.update_property(
            [Gtk.AccessibleProperty.LABEL], [_("Live serial plot")]
        )
        self.plot_area.set_draw_func(self.draw_plot)

        root.append(self.plot_area)

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
        if self._refresh_source_id is None:
            self._refresh_source_id = GLib.timeout_add(16, self.refresh_pending)

    def refresh_pending(self):
        self._refresh_source_id = None
        self.refresh()
        return False

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
        self.plot_area.queue_draw()

    def draw_plot(self, area, context, width, height):
        series = [
            list(values)
            for values in self.plot_data.series.values()
            if values
        ]
        left, right, top, bottom = 72, 20, 20, 52
        plot_width = max(1, width - left - right)
        plot_height = max(1, height - top - bottom)
        foreground = self.get_style_context().get_color()
        context.set_source_rgba(
            foreground.red, foreground.green, foreground.blue, 0.2
        )
        context.set_line_width(1)

        for tick in range(5):
            y = top + plot_height * tick / 4
            context.move_to(left, y)
            context.line_to(width - right, y)
        context.stroke()

        context.set_source_rgba(
            foreground.red, foreground.green, foreground.blue, 0.6
        )
        context.move_to(left, top)
        context.line_to(left, top + plot_height)
        context.line_to(width - right, top + plot_height)
        context.stroke()

        series_colors = self._series_colors()
        flat_values = [value for values in series for value in values]
        if flat_values:
            value_scale = max(1.0, abs(min(flat_values)), abs(max(flat_values)))
            minimum = min(flat_values) / value_scale
            maximum = max(flat_values) / value_scale
            value_range = maximum - minimum
            padding = (
                value_range * 0.05
                if value_range
                else max(0.05, abs(maximum) * 0.05)
            )
            minimum -= padding
            maximum += padding

            for series_index, values in enumerate(series):
                color = self._rgb_color(series_colors[series_index])
                context.set_source_rgba(*(component / 255 for component in color))
                context.set_line_width(2)

                for index, value in enumerate(values):
                    x = left + plot_width * index / max(1, len(values) - 1)
                    scaled_value = value / value_scale
                    y = top + plot_height * (
                        (maximum - scaled_value) / (maximum - minimum)
                    )
                    if index == 0:
                        context.move_to(x, y)
                    else:
                        context.line_to(x, y)

                if len(values) == 1:
                    x = left
                    y = top + plot_height * (
                        (maximum - values[0] / value_scale)
                        / (maximum - minimum)
                    )
                    context.arc(x, y, 2.5, 0, 2 * 3.141592653589793)
                    context.fill()
                else:
                    context.stroke()

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
