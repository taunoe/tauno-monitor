import gettext

import gi
gi.require_version('Adw', '1')
gi.require_version('Gtk', '4.0')

from gi.repository import Adw, GLib, Gtk
from html import escape
from matplotlib.backends.backend_gtk4agg import FigureCanvasGTK4Agg
from matplotlib.figure import Figure
from .plot_chart import series_colors, update_axes

_ = gettext.gettext


class TaunoPlotView(Gtk.Box):
    def __init__(self, plot_data):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.plot_data = plot_data
        self._refresh_source_id = None
        self._visible_samples = 100

        controls = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=12
        )
        controls.set_margin_start(12)
        controls.set_margin_end(12)
        controls.set_margin_bottom(6)
        self.append(controls)

        plot_type_label = Gtk.Label(label=_("Plot type"), xalign=0)
        controls.append(plot_type_label)

        self.plot_type_dropdown = Gtk.DropDown.new(
            Gtk.StringList.new([_("Timeline"), _("Bar chart"), _("Pie chart")]),
            None,
        )
        self.plot_type_dropdown.set_tooltip_text(_("Choose how to display the data."))
        self.plot_type_dropdown.update_property(
            [Gtk.AccessibleProperty.LABEL], [_("Plot type")]
        )
        self.plot_type_dropdown.connect(
            "notify::selected", self._on_plot_type_changed
        )
        controls.append(self.plot_type_dropdown)
        self._plot_type = "timeline"

        self.visible_samples_label = Gtk.Label(
            label=_("Visible samples"), xalign=0
        )
        controls.append(self.visible_samples_label)

        self.visible_samples_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 0, 800, 1
        )
        self.visible_samples_scale.set_hexpand(True)
        self.visible_samples_scale.set_digits(0)
        self.visible_samples_scale.set_draw_value(True)
        self.visible_samples_scale.set_value(self._visible_samples)
        self.visible_samples_scale.set_tooltip_text(
            _("Choose how many recent samples to show; 0 shows all retained samples.")
        )
        self.visible_samples_scale.update_property(
            [Gtk.AccessibleProperty.LABEL], [_("Visible samples")]
        )
        self.visible_samples_scale.connect(
            "value-changed", self._on_visible_samples_changed
        )
        controls.append(self.visible_samples_scale)

        self.figure = Figure(figsize=(3.2, 2.4))
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasGTK4Agg(self.figure)
        self.canvas.set_hexpand(True)
        self.canvas.set_vexpand(True)
        self.canvas.set_margin_start(12)
        self.canvas.set_margin_end(12)
        self.canvas.set_margin_top(12)
        self.canvas.set_accessible_role(Gtk.AccessibleRole.IMG)
        self.canvas.update_property(
            [Gtk.AccessibleProperty.LABEL], [_("Live serial plot")]
        )
        self.append(self.canvas)

        self.legend_label = Gtk.Label(xalign=0)
        self.legend_label.set_use_markup(True)
        self.legend_label.set_wrap(True)
        self.legend_label.set_margin_start(12)
        self.legend_label.set_margin_end(12)
        self.append(self.legend_label)

        self.status_label = Gtk.Label(xalign=1)
        self.status_label.set_margin_start(12)
        self.status_label.set_margin_end(12)
        self.status_label.set_margin_top(6)
        self.status_label.set_margin_bottom(12)
        self.append(self.status_label)

        self.set_hexpand(True)
        self.set_vexpand(True)
        self._style_manager = Adw.StyleManager.get_default()
        self._style_manager.connect_object(
            "notify::dark", self._on_theme_changed, self
        )
        self.refresh()

    def queue_refresh(self):
        if self._refresh_source_id is None:
            self._refresh_source_id = GLib.timeout_add(16, self.refresh_pending)

    def refresh_pending(self):
        self._refresh_source_id = None
        self.refresh()
        return False

    def _on_theme_changed(self, *_args):
        self.refresh()

    def _on_visible_samples_changed(self, scale):
        self._visible_samples = int(scale.get_value())
        self.refresh()

    def _on_plot_type_changed(self, dropdown, _property):
        plot_types = ("timeline", "bar", "pie")
        selected = dropdown.get_selected()
        self._plot_type = (
            plot_types[selected] if selected < len(plot_types) else "timeline"
        )
        show_visible_samples = self._plot_type == "timeline"
        self.visible_samples_label.set_visible(show_visible_samples)
        self.visible_samples_scale.set_visible(show_visible_samples)
        self.refresh()

    def refresh(self):
        series = self.plot_data.series
        series_count = len(series)
        sample_count = sum(len(values) for values in series.values())
        self.status_label.set_text(
            _("Series: {series} · Samples: {samples}").format(
                series=series_count, samples=sample_count
            )
        )
        dark = self._style_manager.get_dark()
        colors = series_colors(dark)
        background = "#242424" if dark else "#ffffff"
        foreground = "#f6f5f4" if dark else "#2e3436"
        legend = [
            f'<span foreground="{colors[index]}">■</span> {escape(label)}'
            for index, label in enumerate(series)
        ]
        self.legend_label.set_markup("    ".join(legend))
        update_axes(
            self.axes,
            series,
            colors,
            foreground,
            background,
            self._visible_samples,
            self._plot_type,
        )
        self.canvas.draw_idle()
