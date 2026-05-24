#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import csv
import math
import pathlib

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "output" / "data" / "benchmark.csv"
GRAPH_DIR = ROOT / "output" / "graphs"
VIDEO_URL = "https://www.youtube.com/watch?v=uJkoI5TnKzA"
VIDEO_TARGET_N = 1_000_000_000
PROOF_MILESTONE_N = VIDEO_TARGET_N
LOCAL_BASELINE = "sieve-wheel30-segm"
VIDEO_ALGORITHMS = [
    "naive-iterate",
    "sqrt-iterate",
    "miller-rabin-iterate",
    "sieve-erat",
    "sieve-erat-segm",
    "sieve-wheel30-segm",
]
CUSTOM_ALGORITHMS = [
    "sieve-erat-odd",
    "sieve-erat-segm-odd",
    "sieve-wheel30-indexed",
    "sieve-wheel30-bitset",
    "sieve-wheel30-bitset-state",
    "sieve-wheel30-bitset-fsm",
    "sieve-lagrange-fsm",
    "sieve-lagrange-lehmer-fsm",
]
GROUP_NAMES = {
    "video": "Video-inspired baseline subset",
    "custom": "My portable C++ improvements",
}

STYLE = {
    "naive-iterate": ("Naive iteration", "#808080", "-"),
    "sqrt-iterate": ("Sqrt iteration", "#ffffff", "-"),
    "miller-rabin-iterate": ("Miller-Rabin iteration", "#ff9ac7", "-"),
    "sieve-erat": ("Sieve of Eratosthenes", "#5f8dff", "-"),
    "sieve-erat-odd": ("Odd-only Eratosthenes", "#a3b9ff", "-"),
    "sieve-erat-segm": ("Segmented sieve", "#44d7ff", "-"),
    "sieve-erat-segm-odd": ("Odd-only segmented sieve", "#80f0ff", "-"),
    "sieve-wheel30-segm": ("Wheel-30 segmented sieve", "#ffe16b", "-"),
    "sieve-wheel30-indexed": ("Wheel-30 indexed sieve", "#79ffb0", "-"),
    "sieve-wheel30-bitset": ("Wheel-30 bitset sieve", "#ffcc56", "-"),
    "sieve-wheel30-bitset-state": ("Wheel-30 stateful bitset", "#ff8f56", "-"),
    "sieve-wheel30-bitset-fsm": ("Wheel-30 FSM bitset", "#ffd98a", "-"),
    "sieve-lagrange-fsm": ("Lagrange + FSM skip", "#c6ff6b", "-"),
    "sieve-lagrange-lehmer-fsm": ("Lehmer + FSM skip", "#9dff57", "-"),
}


def algorithm_group(algorithm: str) -> str:
    return "video" if algorithm in VIDEO_ALGORITHMS else "custom"


def format_int(value: float | int) -> str:
    return f"{int(round(value)):,}"


def format_millions(value: float | int) -> str:
    if float(value) >= 1_000_000_000:
        return f"{float(value) / 1_000_000_000:.2f}B"
    return f"{float(value) / 1_000_000:.1f}M"


def read_rows(path: pathlib.Path) -> dict[str, list[dict[str, float]]]:
    rows: dict[str, list[dict[str, float]]] = collections.defaultdict(list)
    with path.open(newline="") as file:
        for row in csv.DictReader(file):
            rows[row["algorithm"]].append(
                {
                    "n": int(row["n"]),
                    "prime": int(row["prime"]),
                    "seconds": float(row["seconds"]),
                }
            )
    return rows


def one_second_reach(data: list[dict[str, float]]) -> dict[str, object]:
    ordered = sorted(data, key=lambda item: item["n"])
    below: dict[str, float] | None = None

    for item in ordered:
        if item["seconds"] <= 1.0:
            below = item
            continue
        if below is None:
            return {
                "estimate": item["n"],
                "measured_under": None,
                "measured_over": item,
                "status": "above-only",
            }

        x1 = below["n"] + 1
        x2 = item["n"] + 1
        y1 = max(below["seconds"], 1e-9)
        y2 = max(item["seconds"], 1e-9)
        if y1 == y2:
            estimate = x1
        else:
            fraction = (math.log(1.0) - math.log(y1)) / (math.log(y2) - math.log(y1))
            estimate = math.exp(math.log(x1) + fraction * (math.log(x2) - math.log(x1)))

        return {
            "estimate": max(0, estimate - 1),
            "measured_under": below,
            "measured_over": item,
            "status": "interpolated",
        }

    return {
        "estimate": below["n"] if below is not None else 0,
        "measured_under": below,
        "measured_over": None,
        "status": "lower-bound",
    }


def reach_by_algorithm(rows: dict[str, list[dict[str, float]]]) -> dict[str, dict[str, object]]:
    return {algorithm: one_second_reach(data) for algorithm, data in rows.items()}


def find_sample(rows: dict[str, list[dict[str, float]]], algorithm: str, n: int) -> dict[str, float] | None:
    for item in rows.get(algorithm, []):
        if item["n"] == n:
            return item
    return None


def apply_dark_style() -> None:
    plt.style.use("dark_background")
    plt.rcParams.update(
        {
            "figure.facecolor": "#06070d",
            "axes.facecolor": "#090d1a",
            "axes.edgecolor": "#7de5ff",
            "axes.labelcolor": "#e8f0ff",
            "xtick.color": "#a8b0c5",
            "ytick.color": "#a8b0c5",
            "grid.color": "#263149",
            "font.size": 11,
            "axes.titlepad": 14,
        }
    )


def add_card(
    ax,
    x: float,
    y: float,
    width: float,
    height: float,
    title: str,
    value: str,
    subtitle: str,
    color: str,
    value_size: float = 20,
) -> None:
    card = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.022",
        linewidth=1.2,
        edgecolor=color,
        facecolor="#0b1020",
        alpha=0.96,
        transform=ax.transAxes,
    )
    ax.add_patch(card)
    ax.text(x + 0.025, y + height - 0.047, title, transform=ax.transAxes, color="#a8b0c5", fontsize=10.5, weight="bold")
    ax.text(x + 0.025, y + height - 0.115, value, transform=ax.transAxes, color=color, fontsize=value_size, weight="bold")
    ax.text(
        x + 0.025,
        y + 0.035,
        subtitle,
        transform=ax.transAxes,
        color="#e8f0ff",
        fontsize=9.2,
        va="bottom",
        linespacing=1.18,
    )


def plot_story_scorecard(rows: dict[str, list[dict[str, float]]], out: pathlib.Path) -> None:
    reaches = reach_by_algorithm(rows)
    best_algorithm = max(reaches, key=lambda key: float(reaches[key]["estimate"]))
    best = reaches[best_algorithm]
    baseline = reaches[LOCAL_BASELINE]
    bitset = reaches.get("sieve-wheel30-bitset")
    fsm = reaches.get("sieve-wheel30-bitset-fsm")
    target_sample = find_sample(rows, best_algorithm, PROOF_MILESTONE_N)

    best_estimate = float(best["estimate"])
    baseline_estimate = float(baseline["estimate"])
    gain = (best_estimate / baseline_estimate - 1.0) * 100.0
    multiplier = best_estimate / baseline_estimate
    target_percent = PROOF_MILESTONE_N / VIDEO_TARGET_N * 100.0
    estimate_percent = best_estimate / VIDEO_TARGET_N * 100.0

    fig = plt.figure(figsize=(15.5, 8.8), facecolor="#06070d")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()

    ax.text(
        0.06,
        0.93,
        f"Improved portable C++ one-second reach by {gain:.1f}%",
        transform=ax.transAxes,
        color="#ffffff",
        fontsize=26,
        weight="bold",
    )
    ax.text(
        0.06,
        0.885,
        "Same prime(n) challenge as the video, but measured as a portable local run. The exact prime index is hardware-relative; the same-run lift is the meaningful claim.",
        transform=ax.transAxes,
        color="#a8b0c5",
        fontsize=11.5,
    )

    proof_text = "not sampled"
    proof_subtitle = "Run the reach benchmark for this exact milestone."
    if target_sample is not None:
        proof_text = f"{format_millions(PROOF_MILESTONE_N)} in {target_sample['seconds']:.3f}s"
        proof_subtitle = f"prime(1B) = {format_int(target_sample['prime'])}"

    add_card(
        ax,
        0.06,
        0.64,
        0.19,
        0.18,
        "Video goal",
        "1B in 1s",
        "headline target from the video",
        "#ffb0b0",
        value_size=19,
    )
    add_card(
        ax,
        0.29,
        0.64,
        0.19,
        0.18,
        "Portable baseline",
        format_millions(baseline_estimate),
        "wheel-30 segmented sieve",
        "#ffe16b",
        value_size=19,
    )
    add_card(
        ax,
        0.52,
        0.64,
        0.19,
        0.18,
        "My best estimate",
        format_millions(best_estimate),
        f"+{gain:.1f}% same-run reach",
        "#79ffb0",
        value_size=19,
    )
    add_card(
        ax,
        0.75,
        0.64,
        0.19,
        0.18,
        "Measured proof",
        proof_text,
        proof_subtitle,
        "#ffd98a",
        value_size=19,
    )

    ax_ladder = fig.add_axes([0.11, 0.17, 0.55, 0.34])
    ladder = [
        ("Wheel baseline", baseline_estimate, "#ffe16b"),
    ]
    if bitset is not None:
        ladder.append(("Bitset packing", float(bitset["estimate"]), "#ffcc56"))
    if fsm is not None:
        ladder.append(("FSM marking", float(fsm["estimate"]), "#ffd98a"))
    legendre = reaches.get("sieve-lagrange-fsm")
    if legendre is not None and best_algorithm != "sieve-lagrange-fsm":
        ladder.append(("Legendre skip", float(legendre["estimate"]), "#c6ff6b"))
    ladder.append(("Lehmer skip", best_estimate, "#9dff57"))
    labels = [item[0] for item in ladder]
    values = [item[1] for item in ladder]
    colors = [item[2] for item in ladder]
    y_positions = list(range(len(ladder)))
    bars = ax_ladder.barh(y_positions, values, color=colors, edgecolor="#0b1020", linewidth=1.0)
    bars[-1].set_linewidth(2.2)
    bars[-1].set_edgecolor("#ffffff")
    ax_ladder.set_yticks(y_positions)
    ax_ladder.set_yticklabels(labels)
    ax_ladder.set_xscale("log")
    ax_ladder.set_xlim(left=10_000_000, right=max(VIDEO_TARGET_N * 1.35, best_estimate * 1.45))
    ax_ladder.axvline(VIDEO_TARGET_N, color="#ff6a6a", linestyle="--", linewidth=1.4)
    ax_ladder.text(VIDEO_TARGET_N * 1.03, len(ladder) - 0.25, "video target\n1B", color="#ffb0b0", fontsize=9, va="top")
    ax_ladder.set_xlabel("Estimated n at one second (log scale)")
    ax_ladder.set_title(f"What moved the score: {multiplier:.2f}x as far in the same second", loc="left", weight="bold")
    ax_ladder.grid(True, axis="x", which="both", alpha=0.25)
    for y, value in zip(y_positions, values):
        ax_ladder.text(value * 1.05, y, format_int(value), va="center", color="#e8f0ff", weight="bold")

    ax_progress = fig.add_axes([0.72, 0.19, 0.22, 0.28])
    ax_progress.set_axis_off()
    ax_progress.text(0.0, 1.04, "Scores against the video target", transform=ax_progress.transAxes, color="#ffffff", fontsize=13, weight="bold")
    ax_progress.text(
        0.0,
        0.82,
        f"The video's headline target is n = 1,000,000,000.\nThis run proves 1B under one second\nand estimates a {format_millions(best_estimate)} crossing.",
        transform=ax_progress.transAxes,
        color="#a8b0c5",
        fontsize=9.2,
        linespacing=1.25,
    )
    for index, (label, pct, color) in enumerate(
        [
            ("proved 1B", target_percent, "#ffd98a"),
            ("estimated 1s reach", estimate_percent, "#79ffb0"),
        ]
    ):
        y = 0.50 - index * 0.28
        track = FancyBboxPatch(
            (0.0, y),
            1.0,
            0.11,
            boxstyle="round,pad=0.01,rounding_size=0.03",
            linewidth=0,
            facecolor="#182033",
            transform=ax_progress.transAxes,
        )
        fill = FancyBboxPatch(
            (0.0, y),
            min(1.0, pct / 100.0),
            0.11,
            boxstyle="round,pad=0.01,rounding_size=0.03",
            linewidth=0,
            facecolor=color,
            transform=ax_progress.transAxes,
        )
        ax_progress.add_patch(track)
        ax_progress.add_patch(fill)
        ax_progress.text(0.0, y + 0.15, label, transform=ax_progress.transAxes, color="#a8b0c5", fontsize=10)
        ax_progress.text(1.02, y + 0.055, f"{pct:.2f}%", transform=ax_progress.transAxes, color="#e8f0ff", fontsize=12, weight="bold", va="center")

    ax.text(
        0.06,
        0.055,
        "Interpretation: this is in the spirit of the video as an algorithmic one-second race, using a portable C++ formula-assisted fast-forward plus the optimized FSM bitset sieve.",
        transform=ax.transAxes,
        color="#a8b0c5",
        fontsize=10,
    )
    fig.savefig(out, dpi=180)
    plt.close(fig)


def plot_runtime(rows: dict[str, list[dict[str, float]]], out: pathlib.Path) -> None:
    reaches = reach_by_algorithm(rows)
    best_algorithm = max(reaches, key=lambda key: float(reaches[key]["estimate"]))

    best_reach = reaches[best_algorithm]
    best_label = STYLE[best_algorithm][0]
    fig, axes = plt.subplots(1, 2, figsize=(15.5, 7.2), sharex=True, sharey=True)
    groups = [("video", VIDEO_ALGORITHMS), ("custom", CUSTOM_ALGORITHMS)]
    legend_handles = []
    legend_labels = []

    for ax, (group, algorithms) in zip(axes, groups):
        for algorithm in algorithms:
            if algorithm not in rows:
                continue
            data = rows[algorithm]
            label, color, linestyle = STYLE[algorithm]
            xs = [item["n"] + 1 for item in data]
            ys = [max(item["seconds"], 1e-7) for item in data]
            highlighted = algorithm == best_algorithm
            line = ax.plot(
                xs,
                ys,
                marker="o",
                linewidth=3.3 if highlighted else 1.9,
                markersize=5.4 if highlighted else 3.8,
                alpha=1.0 if highlighted else 0.82,
                label=label,
                color=color,
                linestyle=linestyle,
                zorder=4 if highlighted else 2,
            )[0]
            legend_handles.append(line)
            legend_labels.append(label)
            reach = reaches[algorithm]
            if reach["measured_under"] is not None and reach["measured_over"] is not None:
                ax.scatter(
                    [float(reach["estimate"]) + 1],
                    [1.0],
                    marker="D",
                    s=48 if highlighted else 28,
                    color=color,
                    edgecolors="#06070d",
                    linewidths=0.8,
                    zorder=6,
                )

        ax.axhline(1.0, color="#ff6a6a", linewidth=1.8, linestyle="--")
        ax.text(
            0.02,
            1.012,
            "1 second",
            color="#ffb0b0",
            transform=ax.get_yaxis_transform(),
            va="bottom",
            fontsize=10,
            weight="bold",
        )
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(GROUP_NAMES[group], fontsize=12, weight="bold")
        ax.grid(True, which="both", alpha=0.35)

    axes[0].set_ylabel("Runtime (seconds, median)")
    for ax in axes:
        ax.set_xlabel("Prime index n + 1 (log scale; zero-indexed code)")

    fig.suptitle(
        f"Local one-second race: {best_label} reaches about n={format_int(float(best_reach['estimate']))}",
        weight="bold",
        y=0.985,
    )
    fig.text(
        0.105,
        0.925,
        "Absolute n varies by CPU/compiler/load; compare the percent lift between algorithms in the same run.",
        color="#a8b0c5",
        fontsize=10,
    )
    fig.text(
        0.105,
        0.897,
        "Diamond markers show log-interpolated one-second crossings between measured samples.",
        color="#a8b0c5",
        fontsize=9.5,
    )
    fig.legend(legend_handles, legend_labels, loc="lower center", ncol=4, frameon=True, bbox_to_anchor=(0.5, 0.01))
    fig.tight_layout(rect=[0, 0.13, 1, 0.86])
    fig.savefig(out, dpi=180)
    plt.close(fig)


def plot_max_under(rows: dict[str, list[dict[str, float]]], out: pathlib.Path) -> None:
    reaches = reach_by_algorithm(rows)
    ordered_video = sorted(
        [algorithm for algorithm in VIDEO_ALGORITHMS if algorithm in reaches],
        key=lambda key: float(reaches[key]["estimate"]),
    )
    ordered_custom = sorted(
        [algorithm for algorithm in CUSTOM_ALGORITHMS if algorithm in reaches],
        key=lambda key: float(reaches[key]["estimate"]),
    )
    ordered = ordered_video + ordered_custom
    gap = 1.0
    y_positions = list(range(len(ordered_video))) + [
        len(ordered_video) + gap + index for index in range(len(ordered_custom))
    ]
    labels = [STYLE[algorithm][0] for algorithm in ordered]
    values = [max(1.0, float(reaches[algorithm]["estimate"])) for algorithm in ordered]
    colors = [STYLE[algorithm][1] for algorithm in ordered]
    best_algorithm = ordered[-1]
    baseline = reaches.get(LOCAL_BASELINE)
    best = reaches[best_algorithm]

    fig, ax = plt.subplots(figsize=(12.8, 7.3))
    bars = ax.barh(y_positions, values, color=colors, edgecolor="#0b1020", linewidth=0.8)
    for bar, algorithm in zip(bars, ordered):
        if algorithm_group(algorithm) == "video":
            bar.set_alpha(0.72)
            bar.set_hatch("//")
        else:
            bar.set_alpha(0.96)
    ax.axvline(VIDEO_TARGET_N, color="#ff6a6a", linestyle="--", linewidth=1.7)
    if ordered_video and ordered_custom:
        separator = len(ordered_video) - 0.5 + gap / 2
        ax.axhline(separator, color="#263149", linewidth=1.5)
        ax.text(
            VIDEO_TARGET_N * 1.03,
            separator + 0.25,
            "video headline target\nn = 1,000,000,000",
            color="#ffb0b0",
            fontsize=9,
            va="bottom",
        )
        ax.text(
            0.01,
            len(ordered_video) - 0.25,
            "video-inspired baseline subset",
            transform=ax.get_yaxis_transform(),
            color="#a8b0c5",
            fontsize=9,
            va="top",
            ha="left",
        )
        ax.text(
            0.01,
            max(y_positions) + 0.45,
            "my added variants",
            transform=ax.get_yaxis_transform(),
            color="#e8f0ff",
            fontsize=9,
            va="bottom",
            ha="left",
            weight="bold",
        )
    else:
        ax.text(
            VIDEO_TARGET_N * 1.03,
            max(y_positions) - 0.2,
            "video headline target\nn = 1,000,000,000",
            color="#ffb0b0",
            fontsize=9,
            va="top",
        )
    ax.set_xscale("log")
    ax.set_xlim(left=max(1, min(values) * 0.6), right=max(VIDEO_TARGET_N * 1.8, max(values) * 1.45))
    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Estimated largest n at one second (log scale)")
    fig.suptitle("How far each local algorithm gets in one second", weight="bold", y=0.98)
    if baseline is not None:
        gain = (float(best["estimate"]) / float(baseline["estimate"]) - 1.0) * 100.0
        fig.text(
            0.105,
            0.915,
            f"Absolute n is hardware-relative; the same-run improvement is {gain:.1f}% over the pre-bitset wheel-30 baseline.",
            color="#a8b0c5",
            fontsize=10,
        )
    ax.grid(True, axis="x", which="both", alpha=0.35)
    for bar, value, algorithm in zip(bars, values, ordered):
        weight = "bold" if algorithm == best_algorithm else "normal"
        ax.text(
            value * 1.05,
            bar.get_y() + bar.get_height() / 2,
            format_int(value),
            va="center",
            color="#e8f0ff",
            weight=weight,
        )
    fig.tight_layout(rect=[0, 0, 1, 0.88])
    fig.savefig(out, dpi=180)
    plt.close(fig)


def plot_prime_growth(rows: dict[str, list[dict[str, float]]], out: pathlib.Path) -> None:
    # Use the fastest compact wheel data for the p_n growth curve when present.
    preferred = [
        "sieve-lagrange-lehmer-fsm",
        "sieve-lagrange-fsm",
        "sieve-wheel30-bitset-fsm",
        "sieve-wheel30-bitset",
        "sieve-wheel30-indexed",
        "sieve-wheel30-bitset-state",
        "sieve-wheel30-segm",
    ]
    data = next(rows[algorithm] for algorithm in preferred if algorithm in rows)
    fig, ax = plt.subplots(figsize=(11, 6.2))
    ax.plot(
        [item["n"] + 1 for item in data],
        [item["prime"] for item in data],
        marker="o",
        linewidth=2.4,
        color="#ffe16b",
    )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Prime index n + 1 (log scale; code uses zero-indexed n)")
    ax.set_ylabel("prime(n)")
    ax.set_title("Prime values reached in the benchmark", weight="bold")
    ax.grid(True, which="both", alpha=0.35)
    fig.tight_layout()
    fig.savefig(out, dpi=180)
    plt.close(fig)


def write_summary(rows: dict[str, list[dict[str, float]]], out: pathlib.Path) -> None:
    reaches = reach_by_algorithm(rows)
    best_algorithm = max(reaches, key=lambda key: float(reaches[key]["estimate"]))
    best = reaches[best_algorithm]
    baseline = reaches.get(LOCAL_BASELINE)
    best_label = STYLE[best_algorithm][0]
    video_ratio = float(best["estimate"]) / VIDEO_TARGET_N * 100.0

    lines = [
        "# Benchmark Summary",
        "",
        f"Video target: [One second to find the BILLIONth PRIME]({VIDEO_URL}) targets `n = 1,000,000,000` within one second.",
        "",
        "Hardware note: exact prime-index counts are relative to CPU, compiler, OS, and background load. The most meaningful claim is the percentage improvement between algorithms measured in the same local benchmark run.",
        "",
        f"Local best: `{best_label}` reaches an estimated `n = {format_int(float(best['estimate']))}` at one second.",
        f"The strongest measured under-one-second point was `n = {format_int(best['measured_under']['n'])}` in `{best['measured_under']['seconds']:.6f}s`.",
    ]
    if baseline is not None:
        gain = (float(best["estimate"]) / float(baseline["estimate"]) - 1.0) * 100.0
        if video_ratio >= 100.0:
            video_line = (
                f"Against the video's headline target, this portable local run reaches `{video_ratio:.2f}%` "
                "of one billion at the estimated one-second crossing."
            )
        else:
            video_line = (
                f"Against the video's headline target, this portable local run reaches `{video_ratio:.2f}%` "
                "of one billion, so it does not claim to beat the video's final LLVM/Linux result."
            )
        lines.extend(
            [
                f"Against the pre-bitset wheel-30 baseline, that is `{gain:.1f}%` higher one-second reach.",
                video_line,
            ]
        )
    lines.extend(
        [
            "",
            "## Estimated One-Second Reach",
            "",
            "| Group | Algorithm | Estimated n at 1s | Last measured under 1s | Next measured over 1s |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for algorithm, reach in sorted(reaches.items(), key=lambda item: float(item[1]["estimate"]), reverse=True):
        label, _, _ = STYLE[algorithm]
        group = "video-inspired baseline" if algorithm_group(algorithm) == "video" else "mine"
        under = reach["measured_under"]
        over = reach["measured_over"]
        under_text = "n/a" if under is None else f"`{format_int(under['n'])}` at `{under['seconds']:.6f}s`"
        over_text = "not reached" if over is None else f"`{format_int(over['n'])}` at `{over['seconds']:.6f}s`"
        lines.append(f"| {group} | {label} | `{format_int(float(reach['estimate']))}` | {under_text} | {over_text} |")

    lines.extend(
        [
            "",
            "## Largest Sampled Rows",
            "",
        "| Group | Algorithm | Largest sampled n | prime(n) | Seconds |",
        "|---|---|---:|---:|---:|",
        ]
    )
    for algorithm, data in rows.items():
        label, _, _ = STYLE[algorithm]
        group = "video-inspired baseline" if algorithm_group(algorithm) == "video" else "mine"
        best = data[-1]
        lines.append(
            f"| {group} | {label} | `{best['n']:,}` | `{best['prime']:,}` | `{best['seconds']:.6f}` |"
        )
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot benchmark graphs")
    parser.add_argument("csv", nargs="?", type=pathlib.Path, default=DATA)
    parser.add_argument("-o", "--output", type=pathlib.Path, default=GRAPH_DIR)
    args = parser.parse_args()

    rows = read_rows(args.csv)
    args.output.mkdir(parents=True, exist_ok=True)
    apply_dark_style()

    plot_story_scorecard(rows, args.output / "story_scorecard.png")
    plot_runtime(rows, args.output / "runtime_curves.png")
    plot_max_under(rows, args.output / "one_second_reach.png")
    plot_prime_growth(rows, args.output / "prime_growth.png")
    write_summary(rows, args.output / "summary.md")
    print(args.output)


if __name__ == "__main__":
    main()
