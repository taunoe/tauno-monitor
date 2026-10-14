LIGHT_SERIES_COLORS = (
    "#1c71d8",
    "#c64600",
    "#26a269",
    "#9141ac",
    "#9c6f00",
    "#e66100",
    "#3584e4",
    "#c01c28",
    "#1a5fb4",
    "#813d9c",
    "#5e5c64",
    "#a51d2d",
    "#865e3c",
    "#5e5c64",
    "#c64600",
    "#1a5fb4",
)

DARK_SERIES_COLORS = (
    "#78aeed",
    "#ff983b",
    "#57e389",
    "#dc8add",
    "#f8e45c",
    "#ff7800",
    "#62a0ea",
    "#ed333b",
    "#26a269",
    "#c061cb",
    "#99c1f1",
    "#ff7b63",
    "#cdab8f",
    "#c0bfbc",
    "#ff983b",
    "#78aeed",
)


def series_colors(dark):
    return DARK_SERIES_COLORS if dark else LIGHT_SERIES_COLORS


def update_axes(
    axes,
    series,
    colors,
    foreground,
    background,
    visible_samples=0,
    plot_type="timeline",
):
    axes.clear()
    axes.figure.patch.set_facecolor(background)
    axes.set_facecolor(background)
    axes.grid(True, color=foreground, alpha=0.2)
    axes.set_axisbelow(True)
    axes.tick_params(axis='both', colors=foreground)
    for spine in axes.spines.values():
        spine.set_color(foreground)
        spine.set_alpha(0.6)

    if plot_type == "pie":
        labels = []
        latest_values = []
        pie_colors = []
        for index, (label, values) in enumerate(series.items()):
            if values:
                labels.append(label)
                latest_values.append(abs(values[-1]))
                pie_colors.append(colors[index])
        if labels:
            if not any(latest_values):
                latest_values = [1] * len(latest_values)
            axes.pie(
                latest_values,
                labels=labels,
                colors=pie_colors,
                textprops={"color": foreground},
            )
        axes.set_aspect("equal")
        axes.grid(False)
    elif plot_type == "bar":
        labels = []
        latest_values = []
        bar_colors = []
        for index, (label, values) in enumerate(series.items()):
            if values:
                labels.append(label)
                latest_values.append(values[-1])
                bar_colors.append(colors[index])
        axes.barh(labels, latest_values, color=bar_colors)
        axes.grid(True, axis='x', color=foreground, alpha=0.2)
        axes.invert_yaxis()
    else:
        for index, values in enumerate(series.values()):
            if values:
                values = list(values)
                if visible_samples:
                    values = values[-visible_samples:]
                axes.plot(
                    range(len(values)),
                    values,
                    color=colors[index],
                    linewidth=2,
                    marker='o' if len(values) == 1 else None,
                    markersize=5,
                )
    axes.margins(x=0.02, y=0.05)
