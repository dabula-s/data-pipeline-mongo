import io
import logging

import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)


def create_bar_plot(data: dict, title: str, x_label: str, y_label: str) -> io.BytesIO:
    """Generate a bar plot from a dictionary and return it as a BytesIO object."""
    plt.figure(figsize=(10, 6))
    sns.barplot(x=list(data.keys()), y=list(data.values()))
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    # Save plot to a BytesIO buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()
    return buffer


def create_pie_plot(data: dict[str, int], title: str) -> io.BytesIO:
    """Generate a pie chart from a dictionary and return it as a BytesIO object."""
    plt.figure(figsize=(8, 8))
    plt.pie(
        list(data.values()),
        labels=list(data.keys()),
        autopct="%1.1f%%",
        startangle=90,
        colors=sns.color_palette("pastel")
    )
    plt.title(title)
    plt.tight_layout()

    # Save plot to a BytesIO buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()
    return buffer


def create_stacked_bar_plot(data: dict[str, dict[str, int]], ports: list[int], title: str, x_label: str,
                            y_label: str) -> io.BytesIO:
    plt.figure(figsize=(12, 6))
    platforms = list(data.keys())
    port_counts = {port: [data[platform].get(str(port), 0) for platform in platforms] for port in ports}

    bottom = None
    for port in ports:
        counts = port_counts[port]
        plt.bar(platforms, counts, label=f"Port {port}", bottom=bottom)
        # Add text labels for each stack segment
        for i, (count, platform) in enumerate(zip(counts, platforms)):
            if count > 0:  # Only label non-zero counts
                height = bottom[i] if bottom is not None else 0
                plt.text(i, height + count / 2, f"Port {port}: {count}", ha="center", va="center", color="white",
                         fontsize=10)
        bottom = counts if bottom is None else [b + c for b, c in zip(bottom, counts)]

    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()
    return buffer
