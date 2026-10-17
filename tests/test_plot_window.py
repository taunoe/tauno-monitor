import unittest

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.colors import to_rgba

from src.plot_chart import series_colors, update_axes


class PlotWindowTests(unittest.TestCase):
    def test_update_axes_plots_series_with_colors_and_single_sample_marker(self):
        figure = Figure()
        FigureCanvasAgg(figure)
        axes = figure.add_subplot(111)
        series = {
            "temperature": [20.0, 21.5],
            "voltage": [3.3],
        }
        colors = series_colors(False)
        foreground = "#202020"

        update_axes(axes, series, colors, foreground, "#ffffff")
        figure.canvas.draw()

        lines = axes.get_lines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(list(lines[0].get_ydata()), [20.0, 21.5])
        self.assertEqual(lines[0].get_color(), colors[0])
        self.assertEqual(list(lines[1].get_ydata()), [3.3])
        self.assertEqual(lines[1].get_marker(), 'o')
        self.assertEqual(lines[1].get_color(), colors[1])
        self.assertEqual(axes.get_facecolor(), to_rgba("#ffffff"))
        self.assertEqual(figure.get_facecolor(), to_rgba("#ffffff"))

    def test_update_axes_clears_previous_series(self):
        figure = Figure()
        FigureCanvasAgg(figure)
        axes = figure.add_subplot(111)
        foreground = "#f6f5f4"
        colors = series_colors(True)
        update_axes(axes, {"old": [1.0]}, colors, foreground, "#242424")

        update_axes(axes, {}, colors, foreground, "#242424")

        self.assertEqual(axes.get_lines(), [])
        self.assertEqual(axes.get_facecolor(), to_rgba("#242424"))
        self.assertEqual(figure.get_facecolor(), to_rgba("#242424"))
        self.assertEqual(
            axes.spines["left"].get_edgecolor(),
            (*to_rgba(foreground)[:3], 0.6),
        )

    def test_series_palettes_are_distinct_for_light_and_dark_themes(self):
        light_colors = series_colors(False)
        dark_colors = series_colors(True)

        self.assertEqual(len(light_colors), 16)
        self.assertEqual(len(dark_colors), 16)
        self.assertNotEqual(light_colors, dark_colors)

    def test_visible_sample_limit_shows_latest_samples(self):
        figure = Figure()
        FigureCanvasAgg(figure)
        axes = figure.add_subplot(111)
        series = {"temperature": list(range(1, 201))}

        update_axes(
            axes,
            series,
            series_colors(False),
            "#202020",
            "#ffffff",
            visible_samples=100,
        )

        line = axes.get_lines()[0]
        self.assertEqual(len(line.get_ydata()), 100)
        self.assertEqual(list(line.get_ydata()), list(range(101, 201)))

    def test_bar_chart_shows_latest_value_for_each_series(self):
        figure = Figure()
        FigureCanvasAgg(figure)
        axes = figure.add_subplot(111)
        series = {
            "temperature": [20.0, 21.5],
            "voltage": [3.3],
            "empty": [],
        }

        update_axes(
            axes,
            series,
            series_colors(False),
            "#202020",
            "#ffffff",
            visible_samples=1,
            plot_type="bar",
        )

        self.assertEqual(
            [bar.get_width() for bar in axes.patches], [21.5, 3.3]
        )
        self.assertEqual(
            [label.get_text() for label in axes.get_yticklabels()],
            ["temperature", "voltage"],
        )
        self.assertEqual(axes.get_lines(), [])

    def test_pie_chart_shows_one_sector_for_each_series(self):
        figure = Figure()
        FigureCanvasAgg(figure)
        axes = figure.add_subplot(111)
        series = {
            "temperature": [20.0, 21.5],
            "voltage": [3.3],
            "empty": [],
        }

        update_axes(
            axes,
            series,
            series_colors(False),
            "#202020",
            "#ffffff",
            plot_type="pie",
        )

        self.assertEqual(len(axes.patches), 2)
        self.assertEqual(
            [label.get_text() for label in axes.texts],
            ["temperature", "voltage"],
        )
        self.assertAlmostEqual(
            axes.patches[0].theta2 - axes.patches[0].theta1,
            360 * 21.5 / 24.8,
            delta=1e-5,
        )

    def test_pie_chart_handles_zero_and_negative_values(self):
        figure = Figure()
        FigureCanvasAgg(figure)
        axes = figure.add_subplot(111)

        update_axes(
            axes,
            {"zero": [0], "negative": [-2]},
            series_colors(False),
            "#202020",
            "#ffffff",
            plot_type="pie",
        )

        self.assertEqual(len(axes.patches), 2)

    def test_histogram_shows_distribution_of_each_nonempty_series(self):
        figure = Figure()
        FigureCanvasAgg(figure)
        axes = figure.add_subplot(111)
        series = {
            "temperature": [1.0, 1.2, 1.4, 1.8],
            "voltage": [3.0, 3.2],
            "empty": [],
        }
        colors = series_colors(False)

        update_axes(
            axes,
            series,
            colors,
            "#202020",
            "#ffffff",
            visible_samples=1,
            plot_type="histogram",
        )
        figure.canvas.draw()

        self.assertEqual(len(axes.patches), 2)
        first_path, second_path = (
            patch.get_path().vertices for patch in axes.patches
        )
        self.assertEqual(list(first_path[:, 0]), list(second_path[:, 0]))
        self.assertEqual(
            sorted((max(path[:, 1]) for path in (first_path, second_path))),
            [2.0, 3.0],
        )
        self.assertEqual(
            {patch.get_facecolor() for patch in axes.patches},
            {to_rgba(colors[0], 0.6), to_rgba(colors[1], 0.6)},
        )
        self.assertEqual(axes.get_lines(), [])

    def test_timeline_restores_auto_aspect_after_pie_chart(self):
        figure = Figure()
        FigureCanvasAgg(figure)
        axes = figure.add_subplot(111)
        colors = series_colors(False)

        update_axes(
            axes,
            {"temperature": [20.0, 21.5]},
            colors,
            "#202020",
            "#ffffff",
            plot_type="pie",
        )
        self.assertEqual(axes.get_aspect(), 1.0)

        update_axes(
            axes,
            {"temperature": [20.0, 21.5]},
            colors,
            "#202020",
            "#ffffff",
            plot_type="timeline",
        )

        self.assertEqual(axes.get_aspect(), "auto")
        self.assertEqual(len(axes.get_lines()), 1)

    def test_zero_visible_sample_limit_shows_all_available_samples(self):
        figure = Figure()
        FigureCanvasAgg(figure)
        axes = figure.add_subplot(111)
        series = {"temperature": [1, 2, 3]}

        update_axes(
            axes,
            series,
            series_colors(False),
            "#202020",
            "#ffffff",
            visible_samples=0,
        )

        self.assertEqual(list(axes.get_lines()[0].get_ydata()), [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
