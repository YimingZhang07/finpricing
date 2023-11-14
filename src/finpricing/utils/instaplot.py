import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import functools

plt.style.use("ggplot")

WRAPPING_ARGS = ["x", "y", "title", "x_label", "y_label", "x_axis_formatter", "y_axis_formatter", "x_tick_labels", "legend", "s", "tight_layout"]

def bps_formatter(x, pos):
    return f"{x*10000:.0f} bps"

def plotting_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        unexpected_kwargs = {k: v for k, v in kwargs.items() if k not in WRAPPING_ARGS}
        fig, ax, res = func(kwargs.get("x"), kwargs.get("y"), **unexpected_kwargs)
        if kwargs.get("title"):
            ax.set_title(kwargs.get("title"))
        if kwargs.get("x_label"):
            ax.set_xlabel(kwargs.get("x_label"))
        if kwargs.get("y_label"):
            ax.set_ylabel(kwargs.get("y_label"))
        if kwargs.get("x_axis_formatter"):
            pass
        if kwargs.get("y_axis_formatter"):
            if kwargs.get("y_axis_formatter") == "percent":
                ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
            if kwargs.get("y_axis_formatter") == "bps":
                ax.yaxis.set_major_formatter(mticker.FuncFormatter(bps_formatter))
        if kwargs.get("x_tick_labels"):
            ax.set_xticks(kwargs.get("x"))
            ax.set_xticklabels(kwargs.get("x_tick_labels"))
        if kwargs.get("legend"):
            ax.legend()
        if kwargs.get("s"):
            values = kwargs.get("s")
            res.set_sizes(values)
        if kwargs.get("tight_layout"):
            fig.tight_layout()
    return wrapper


@plotting_decorator
def plot(
    x,
    y,
    **kwargs
):
    fig, ax = plt.subplots()
    res = ax.plot(x, y, **kwargs)
    return fig, ax, res


@plotting_decorator
def scatter(
    x,
    y,
    **kwargs
):
    fig, ax = plt.subplots()
    res = ax.scatter(x, y, **kwargs)
    return fig, ax, res
