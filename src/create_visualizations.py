"""
Script to generate multi‑dimensional data visualizations for the
CMP_SC‑8630 data visualization assignment.  The script loads three
real‑world datasets related to climate and hydrology and produces
visualizations that explore patterns across multiple variables and
dimensions.  The resulting figures are saved to the ``output``
directory.  The datasets used here include:

* ``weather_data.csv`` – daily weather observations for multiple
  cities in New Zealand (2016–2017) containing temperature,
  humidity, wind, pressure and precipitation variables.  Source:
  mosaicData package within the Rdatasets collection.
* ``global_temp.csv`` – NASA Goddard Institute for Space Studies
  (GISTEMP) global land–ocean temperature anomalies from 1880 to
  2025.  Monthly anomalies relative to the 1951–1980 baseline are
  provided.  Source: NASA GISS via data.giss.nasa.gov.
* ``minnesota_weather.csv`` – monthly weather summary for six
  Minnesota agricultural sites (1927–1936) including cooling and
  heating degree days, precipitation and temperature extremes.
  Source: agridat package within Rdatasets.

The visualizations include heatmaps, scatter plots and line charts
to illustrate how variables such as temperature, humidity and
precipitation vary over time and across different locations.
"""

import os
from typing import List

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import seaborn as sns
import numpy as np


def ensure_output_dir(path: str) -> None:
    """Ensure that the output directory exists."""
    os.makedirs(path, exist_ok=True)


def plot_weather_heatmap(df: pd.DataFrame, outdir: str) -> str:
    """Create a heatmap of average temperature by city and month.

    Parameters
    ----------
    df : pandas.DataFrame
        Weather data with columns ``city``, ``month`` and ``avg_temp``.
    outdir : str
        Directory to write the output image.

    Returns
    -------
    str
        Path to the saved figure.
    """
    monthly_avg = (
        df.groupby(["city", "month"], as_index=False)["avg_temp"].mean()
    )
    heatmap_data = monthly_avg.pivot(index="city", columns="month", values="avg_temp")
    heatmap_data = heatmap_data.reindex(sorted(heatmap_data.columns), axis=1)

    plt.figure(figsize=(10, 4))
    sns.heatmap(
        heatmap_data,
        cmap="coolwarm",
        annot=True,
        fmt=".1f",
        cbar_kws={"label": "Average temperature"},
    )
    plt.title("Average monthly temperature by city")
    plt.xlabel("Month")
    plt.ylabel("City")

    outfile = os.path.join(outdir, "weather_heatmap_2.png")
    plt.tight_layout()
    plt.savefig(outfile, dpi=300)
    plt.close()
    return outfile


def plot_weather_scatter(df: pd.DataFrame, outdir: str) -> str:
    """Create a scatter plot exploring relationships between humidity,
    temperature and precipitation.

    Each point represents a daily observation.  The x‑axis shows
    average humidity, the y‑axis shows average temperature in Fahrenheit,
    the marker size encodes precipitation and colour encodes the city.
    Separate legends are provided for city and precipitation to avoid
    overlap.

    Parameters
    ----------
    df : pandas.DataFrame
        Weather data with columns ``avg_humidity``, ``avg_temp``,
        ``precip`` and ``city``.
    outdir : str
        Directory to write the output image.

    Returns
    -------
    str
        Path to the saved figure.
    """
    plot_df = df.copy()
    plot_df["precip"] = pd.to_numeric(plot_df["precip"], errors="coerce").fillna(0.0)

    plt.figure(figsize=(9, 6))
    size_range = (20, 300)
    city_order = sorted(plot_df["city"].dropna().unique())
    palette = sns.color_palette(n_colors=len(city_order))
    color_map = dict(zip(city_order, palette))

    ax = sns.scatterplot(
        data=plot_df,
        x="avg_humidity",
        y="avg_temp",
        hue="city",
        hue_order=city_order,
        palette=color_map,
        size="precip",
        sizes=size_range,
        alpha=0.65,
        legend=False,
    )

    plt.xlabel("Average relative humidity (%)")
    plt.ylabel("Average temperature (°F)")
    plt.title("Daily weather: temperature vs humidity with precipitation (size)")

    city_handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="",
            markerfacecolor=color_map[city],
            markeredgecolor="none",
            markersize=7,
            label=city,
        )
        for city in city_order
    ]
    legend_city = plt.legend(
        handles=city_handles,
        title="City",
        loc="upper left",
        bbox_to_anchor=(1.02, 1.0),
    )
    ax.add_artist(legend_city)

    precip_max = float(plot_df["precip"].max())
    if precip_max > 0:
        precip_values = np.linspace(0, precip_max, 4)
    else:
        precip_values = np.array([0.0, 0.0, 0.0, 0.0])
    mapped_sizes = np.interp(precip_values, [0, max(precip_max, 1e-9)], size_range)

    size_handles = [
        plt.scatter([], [], s=size, color="gray", alpha=0.65, label=f"{value:.2f}")
        for value, size in zip(precip_values, mapped_sizes)
    ]
    plt.legend(
        handles=size_handles,
        title="Precipitation",
        loc="lower left",
        bbox_to_anchor=(1.02, 0.0),
    )

    outfile = os.path.join(outdir, "weather_scatter_2.png")
    plt.tight_layout()
    plt.savefig(outfile, dpi=300)
    plt.close()
    return outfile


def plot_global_temp_heatmap(df: pd.DataFrame, outdir: str) -> str:
    """Create a heatmap of global temperature anomalies by year and month.

    Parameters
    ----------
    df : pandas.DataFrame
        Global temperature anomalies where rows correspond to years and
        columns to months (Jan–Dec).  The DataFrame should include
        numeric values for anomalies.  Missing values are allowed and
        will appear as blank cells.
    outdir : str
        Directory to write the output image.

    Returns
    -------
    str
        Path to the saved figure.
    """
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    long_df = df.melt(
        id_vars="Year",
        value_vars=months,
        var_name="Month",
        value_name="Anomaly",
    )

    month_to_num = {month: idx for idx, month in enumerate(months, start=1)}
    long_df["MonthNum"] = long_df["Month"].map(month_to_num)
    heatmap_data = long_df.pivot(index="Year", columns="MonthNum", values="Anomaly")
    heatmap_data = heatmap_data.sort_index()

    plt.figure(figsize=(10, 8))
    sns.heatmap(
        heatmap_data,
        cmap="coolwarm",
        vmin=-1.5,
        vmax=1.5,
        cbar_kws={"label": "Temperature anomaly (°C relative to 1951–1980)"},
        linewidths=0,
        linecolor="white",
    )

    plt.xticks(ticks=np.arange(0.5, 12.5, 1), labels=months, rotation=45, ha="right")
    plt.title("Global land–ocean temperature anomalies (1880–2025)")
    plt.xlabel("Month")
    plt.ylabel("Year")

    outfile = os.path.join(outdir, "global_temp_heatmap_2.png")
    plt.tight_layout()
    plt.savefig(outfile, dpi=300)
    plt.close()
    return outfile


def plot_minnesota_precip_line(df: pd.DataFrame, outdir: str) -> str:
    """Create a line chart of monthly precipitation by site over time.

    This figure shows how precipitation varies across the six Minnesota
    sites from 1927 to 1936.  Each line corresponds to a site and
    month; values are aggregated by year and month.

    Parameters
    ----------
    df : pandas.DataFrame
        Minnesota weather data with columns ``site``, ``year``, ``mo`` (month) and
        ``precip``.
    outdir : str
        Directory to write the output image.

    Returns
    -------
    str
        Path to the saved figure.
    """
    plot_df = df.copy()
    plot_df["date"] = pd.to_datetime(
        {"year": plot_df["year"], "month": plot_df["mo"], "day": 1}
    )

    plt.figure(figsize=(10, 6))
    sns.lineplot(data=plot_df, x="date", y="precip", hue="site")
    plt.title("Monthly precipitation by Minnesota site (1927–1936)")
    plt.xlabel("Year")
    plt.ylabel("Precipitation (inches)")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", title="Site")

    outfile = os.path.join(outdir, "minnesota_precip_line_2.png")
    plt.tight_layout()
    plt.savefig(outfile, dpi=300)
    plt.close()
    return outfile


def main() -> List[str]:
    """Run all visualizations and return a list of generated file paths."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    out_dir = os.path.join(base_dir, "output")
    ensure_output_dir(out_dir)
    figures: List[str] = []

    # Load and plot weather data
    weather_path = os.path.join(data_dir, "weather_data.csv")
    weather_df = pd.read_csv(weather_path)
    # Plot heatmap and scatter
    figures.append(plot_weather_heatmap(weather_df, out_dir))
    figures.append(plot_weather_scatter(weather_df, out_dir))

    # Load and plot global temperature anomalies
    global_path = os.path.join(data_dir, "global_temp.csv")
    global_df = pd.read_csv(global_path, skiprows=1)
    # Replace *** with NA and convert to numeric
    global_df = global_df.replace("***", pd.NA)
    for col in global_df.columns[1:]:
        global_df[col] = pd.to_numeric(global_df[col], errors="coerce")
    figures.append(plot_global_temp_heatmap(global_df, out_dir))

    # Load and plot Minnesota weather data
    minn_path = os.path.join(data_dir, "minnesota_weather.csv")
    minn_df = pd.read_csv(minn_path)
    figures.append(plot_minnesota_precip_line(minn_df, out_dir))
    return figures


if __name__ == "__main__":
    generated = main()
    print("Generated figures:")
    for path in generated:
        print(path)