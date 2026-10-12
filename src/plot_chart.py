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
    axes, series, colors, foreground, background, visible_samples=0
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
