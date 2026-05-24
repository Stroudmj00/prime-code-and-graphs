#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import csv
import math
import pathlib

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle


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
    "sieve-lagrange-lehmer-axler-fsm",
    "sieve-lagrange-lehmer-axler-phi7-fsm",
]

GROUP_NAMES = {
    "video": "Video-inspired baseline",
    "custom": "My C++ variants",
}

GROUP_CONFIG = {
    "video": {
        "panel": "#f0f5ff",
        "line": "#3b82f6",
        "accent": "#1d4ed8",
        "bar": "#93c5fd",
    },
    "custom": {
        "panel": "#eefcf3",
        "line": "#16a34a",
        "accent": "#166534",
        "bar": "#86efac",
    },
}

STYLE = {
    "naive-iterate": ("Naive iteration", "#94a3b8", "-"),
    "sqrt-iterate": ("Sqrt iteration", "#64748b", "-"),
    "miller-rabin-iterate": ("Miller-Rabin iteration", "#e11d48", "-"),
    "sieve-erat": ("Sieve of Eratosthenes", "#3b82f6", "-"),
    "sieve-erat-odd": ("Odd-only Eratosthenes", "#60a5fa", "-"),
    "sieve-erat-segm": ("Segmented sieve", "#06b6d4", "-"),
    "sieve-erat-segm-odd": ("Odd-only segmented", "#22d3ee", "-"),
    "sieve-wheel30-segm": ("Wheel-30 segmented", "#f59e0b", "-"),
    "sieve-wheel30-indexed": ("Wheel-30 indexed", "#10b981", "-"),
    "sieve-wheel30-bitset": ("Wheel-30 bitset", "#84cc16", "-"),
    "sieve-wheel30-bitset-state": ("Wheel-30 stateful bitset", "#f97316", "-"),
    "sieve-wheel30-bitset-fsm": ("Wheel-30 FSM bitset", "#fbbf24", "-"),
    "sieve-lagrange-fsm": ("Lagrange + FSM", "#84cc16", "-"),
    "sieve-lagrange-lehmer-fsm": ("Lehmer + pi table FSM", "#22c55e", "-"),
    "sieve-lagrange-lehmer-axler-fsm": ("Lehmer + pi table + Axler", "#15803d", "-"),
    "sieve-lagrange-lehmer-axler-phi7-fsm": ("Lehmer + Axler + phi7", "#047857", "-"),
}

CANVAS_BG = "#f6f8fc"
TEXT_MUTED = "#64748b"


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


def validate_known_algorithms(rows: dict[str, list[dict[str, float]]]) -> None:
    unknown = sorted(set(rows) - set(STYLE))
    if unknown:
        names = ", ".join(unknown)
        raise SystemExit(f"Missing plot styles for benchmark algorithm(s): {names}")


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


def apply_recruiter_style() -> None:
    plt.style.use("default")
    plt.rcParams.update(
        {
            "figure.facecolor": CANVAS_BG,
            "axes.facecolor": "#ffffff",
            "axes.edgecolor": "#cbd5e1",
            "axes.labelcolor": "#0f172a",
            "xtick.color": "#475569",
            "ytick.color": "#475569",
            "grid.color": "#d6deeb",
            "grid.linewidth": 0.8,
            "font.size": 11,
            "font.family": ["DejaVu Sans"],
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.titlepad": 10,
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
        edgecolor=f"{color}77",
        facecolor="#ffffff",
        alpha=1.0,
        transform=ax.transAxes,
    )
    ax.add_patch(card)
    ax.text(
        x + 0.025,
        y + height - 0.047,
        title,
        transform=ax.transAxes,
        color=TEXT_MUTED,
        fontsize=10.5,
        weight="bold",
    )
    ax.text(
        x + 0.025,
        y + height - 0.115,
        value,
        transform=ax.transAxes,
        color="#0f172a",
        fontsize=value_size,
        weight="bold",
    )
    ax.text(
        x + 0.025,
        y + 0.035,
        subtitle,
        transform=ax.transAxes,
        color=TEXT_MUTED,
        fontsize=9,
        va="bottom",
        linespacing=1.16,
    )


def add_group_badge(ax, text: str, color: str, x: float, y: float, width: float = 0.18) -> None:
    badge = FancyBboxPatch(
        (x, y),
        width,
        0.045,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        linewidth=0.9,
        edgecolor=color,
        facecolor="#ffffff",
        transform=ax.transAxes,
    )
    ax.add_patch(badge)
    ax.text(
        x + 0.01,
        y + 0.025,
        text,
        transform=ax.transAxes,
        fontsize=8.8,
        weight="bold",
        color=color,
        va="center",
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

    fig = plt.figure(figsize=(15.5, 8.8), facecolor=CANVAS_BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()

    ax.text(
        0.06,
        0.93,
        f"Portable C++ prime benchmark: same-run comparison",
        transform=ax.transAxes,
        color="#111827",
        fontsize=25,
        weight="bold",
    )
    ax.text(
        0.06,
        0.893,
        "The charts are designed to make lift differences clear at a glance.",
        transform=ax.transAxes,
        color=TEXT_MUTED,
        fontsize=11.5,
    )
    ax.text(
        0.06,
        0.872,
        "Exact n values are hardware-relative; this report uses same-run relative comparisons.",
        transform=ax.transAxes,
        color="#6b7280",
        fontsize=9.7,
    )
    ax.text(
        0.06,
        0.849,
        "Estimated one-second crossings are interpolated and should be treated as directional guidance, not absolute proof.",
        transform=ax.transAxes,
        color="#6b7280",
        fontsize=9.7,
    )

    proof_text = "not sampled"
    proof_subtitle = "Run the reach benchmark at this milestone to confirm."
    if target_sample is not None:
        proof_text = f"{format_millions(PROOF_MILESTONE_N)} in {target_sample['seconds']:.3f}s"
        proof_subtitle = f"prime(1B) = {format_int(target_sample['prime'])}"

    add_card(
        ax,
        0.06,
        0.62,
        0.19,
        0.18,
        "External target",
        "1B in 1s",
        "video headline goal",
        "#ef4444",
        value_size=19,
    )
    add_card(
        ax,
        0.275,
        0.62,
        0.19,
        0.18,
        "Base local",
        format_millions(baseline_estimate),
        "wheel-30 segmented",
        "#f59e0b",
        value_size=19,
    )
    add_card(
        ax,
        0.49,
        0.62,
        0.19,
        0.18,
        "Best local estimate",
        format_millions(best_estimate),
        f"{gain:.1f}% above base",
        "#22c55e",
        value_size=19,
    )
    add_card(
        ax,
        0.705,
        0.62,
        0.24,
        0.18,
        "Measured proof point",
        proof_text,
        proof_subtitle,
        "#8b5cf6",
        value_size=17,
    )

    add_group_badge(ax, "Video target + portable baseline", GROUP_CONFIG["video"]["accent"], 0.06, 0.79, 0.38)
    add_group_badge(ax, "My C++ result", GROUP_CONFIG["custom"]["accent"], 0.49, 0.79, 0.45)

    ax_ladder = fig.add_axes([0.13, 0.18, 0.54, 0.34])
    ax_ladder.set_facecolor("#f8fbff")
    ladder = [("Wheel baseline", baseline_estimate, GROUP_CONFIG["video"]["line"])]
    if bitset is not None:
        ladder.append(("Bitset packing", float(bitset["estimate"]), GROUP_CONFIG["custom"]["line"]))
    if fsm is not None:
        ladder.append(("FSM marking", float(fsm["estimate"]), GROUP_CONFIG["custom"]["line"]))
    legendre = reaches.get("sieve-lagrange-fsm")
    if legendre is not None and best_algorithm != "sieve-lagrange-fsm":
        ladder.append(("Legendre skip", float(legendre["estimate"]), GROUP_CONFIG["custom"]["line"]))
    lehmer = reaches.get("sieve-lagrange-lehmer-fsm")
    if lehmer is not None and best_algorithm not in {"sieve-lagrange-fsm", "sieve-lagrange-lehmer-fsm"}:
        ladder.append(("Lehmer + pi table", float(lehmer["estimate"]), GROUP_CONFIG["custom"]["line"]))
    axler = reaches.get("sieve-lagrange-lehmer-axler-fsm")
    if axler is not None and best_algorithm != "sieve-lagrange-lehmer-axler-fsm":
        ladder.append(("Axler bound", float(axler["estimate"]), GROUP_CONFIG["custom"]["line"]))
    best_label_by_algorithm = {
        "sieve-lagrange-fsm": "Legendre skip",
        "sieve-lagrange-lehmer-fsm": "Lehmer + pi table",
        "sieve-lagrange-lehmer-axler-fsm": "Pi table + Axler",
        "sieve-lagrange-lehmer-axler-phi7-fsm": "Deeper phi table",
    }
    best_label = best_label_by_algorithm.get(best_algorithm, STYLE[best_algorithm][0])
    ladder.append((best_label, best_estimate, GROUP_CONFIG["custom"]["accent"]))

    labels = [item[0] for item in ladder]
    values = [item[1] for item in ladder]
    colors = [item[2] for item in ladder]
    y_positions = list(range(len(ladder)))
    bars = ax_ladder.barh(y_positions, values, color=colors, edgecolor="#ffffff", linewidth=1.1)
    bars[-1].set_linewidth(2.2)
    bars[-1].set_edgecolor("#0f172a")
    ax_ladder.set_yticks(y_positions)
    ax_ladder.set_yticklabels(labels)
    ax_ladder.set_xscale("log")
    ax_ladder.set_xlim(left=10_000_000, right=max(VIDEO_TARGET_N * 1.35, best_estimate * 1.45))
    ax_ladder.axvline(VIDEO_TARGET_N, color="#ef4444", linestyle="--", linewidth=1.4)
    ax_ladder.text(VIDEO_TARGET_N * 1.03, len(ladder) - 0.27, "video target\n1B", color="#ef4444", fontsize=9, va="top")
    ax_ladder.set_xlabel("Estimated n at one second (log scale)")
    ax_ladder.set_title("How each optimization layer contributes to reach", loc="left")
    ax_ladder.grid(True, axis="x", alpha=0.25)
    ladder_right = ax_ladder.get_xlim()[1]
    for y, value in zip(y_positions, values):
        pct = (value / baseline_estimate - 1.0) * 100.0
        inside = value > ladder_right / 3.0
        ax_ladder.text(
            value / 1.08 if inside else value * 1.05,
            y,
            f"{format_int(value)}   ({pct:+.1f}%)",
            va="center",
            ha="right" if inside else "left",
            color="#ffffff" if inside else "#0f172a",
            fontsize=9,
            weight="bold",
        )

    ax_progress = fig.add_axes([0.72, 0.22, 0.23, 0.26])
    ax_progress.set_axis_off()
    ax_progress.set_facecolor("#f8fbff")
    ax_progress.text(0.0, 1.03, "Progress vs. target", transform=ax_progress.transAxes, color="#111827", fontsize=13, weight="bold")
    ax_progress.text(
        0.0,
        0.86,
        f"The target is n = 1,000,000,000.\nThe best estimate is {format_millions(best_estimate)} at one second.",
        transform=ax_progress.transAxes,
        color=TEXT_MUTED,
        fontsize=9.2,
        linespacing=1.2,
    )
    for index, (label, pct, color) in enumerate(
        [
            ("target 1B", target_percent, "#ef4444"),
            ("best estimate", estimate_percent, "#22c55e"),
        ]
    ):
        y = 0.45 - index * 0.28
        track = Rectangle((0.0, y), 1.0, 0.095, linewidth=0, facecolor="#e5ebf6", transform=ax_progress.transAxes)
        fill = Rectangle((0.0, y), min(1.0, pct / 100.0), 0.095, linewidth=0, facecolor=color, transform=ax_progress.transAxes)
        ax_progress.add_patch(track)
        ax_progress.add_patch(fill)
        ax_progress.text(0.0, y + 0.13, label, transform=ax_progress.transAxes, color=TEXT_MUTED, fontsize=9.8)
        ax_progress.text(
            0.98,
            y + 0.055,
            f"{pct:.2f}%",
            transform=ax_progress.transAxes,
            color="#ffffff",
            fontsize=11.5,
            weight="bold",
            va="center",
            ha="right",
        )

    ax.text(
        0.06,
        0.055,
        "Interpretation: this is the same prime-index challenge and same-run context as the video's benchmark format; use this to judge directional relative improvements.",
        transform=ax.transAxes,
        color=TEXT_MUTED,
        fontsize=10,
    )
    fig.savefig(out, dpi=180)
    plt.close(fig)


def _order_group_algorithms(algorithms: list[str], rows: dict[str, list[dict[str, float]]]) -> list[str]:
    return [algorithm for algorithm in algorithms if algorithm in rows]


def plot_runtime(rows: dict[str, list[dict[str, float]]], out: pathlib.Path) -> None:
    reaches = reach_by_algorithm(rows)
    best_algorithm = max(reaches, key=lambda key: float(reaches[key]["estimate"]))

    best_reach = reaches[best_algorithm]
    best_label = STYLE[best_algorithm][0]
    fig, axes = plt.subplots(1, 2, figsize=(15.5, 7.8), sharex=True, sharey=True)
    groups = [("video", VIDEO_ALGORITHMS), ("custom", CUSTOM_ALGORITHMS)]
    legend_handles = []
    legend_labels = []

    for index, (group, algorithms) in enumerate(groups):
        ax = axes[index]
        palette = GROUP_CONFIG[group]
        panel_algorithms = _order_group_algorithms(algorithms, rows)
        ax.set_facecolor(palette["panel"])
        for algorithm in panel_algorithms:
            data = rows[algorithm]
            label, color, linestyle = STYLE[algorithm]
            xs = [item["n"] + 1 for item in data]
            ys = [max(item["seconds"], 1e-7) for item in data]
            highlighted = algorithm == best_algorithm
            line = ax.plot(
                xs,
                ys,
                marker="o",
                linewidth=3.0 if highlighted else 1.9,
                markersize=5.2 if highlighted else 3.8,
                alpha=1.0 if highlighted else 0.84,
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
                    s=52 if highlighted else 28,
                    color=color,
                    edgecolors="#ffffff",
                    linewidths=0.8,
                    zorder=6,
                )
            if highlighted:
                ax.annotate(
                    "winner",
                    xy=(xs[-1], ys[-1]),
                    xytext=(8, 8),
                    textcoords="offset points",
                    color="#166534",
                    fontsize=9,
                    weight="bold",
                    arrowprops={"arrowstyle": "->", "color": "#166534", "lw": 1.0},
                )

        ax.axhline(1.0, color="#ef4444", linewidth=1.5, linestyle="--")
        ax.text(
            0.02,
            1.012,
            "1 second",
            color="#ef4444",
            transform=ax.get_yaxis_transform(),
            va="bottom",
            fontsize=10,
            weight="bold",
        )
        ax.set_xscale("log")
        ax.set_yscale("log")
        subtitle = "video baseline set" if group == "video" else "my added variants"
        ax.set_title(f"{'A' if group == 'video' else 'B'}. {GROUP_NAMES[group]} ({subtitle})", loc="left")
        max_sampled_n = max(item["n"] + 1 for data in rows.values() for item in data)
        runtime_right = max(VIDEO_TARGET_N * 1.4, max_sampled_n * 1.2, float(best_reach["estimate"]) * 1.2)
        ax.set_xlim(100_000, runtime_right)
        ax.grid(True, which="both", alpha=0.35)

    axes[0].set_ylabel("Runtime (seconds)")
    for ax in axes:
        ax.set_xlabel("Prime index n + 1 (log scale; zero-indexed in benchmark)")

    fig.suptitle(
        f"Local one-second race: {best_label} reaches about n={format_int(float(best_reach['estimate']))}",
        weight="bold",
        y=0.985,
    )
    fig.text(
        0.105,
        0.925,
        "Absolute n values are not portable; compare percent and slope differences inside the same local run.",
        color=TEXT_MUTED,
        fontsize=10,
    )
    fig.text(
        0.105,
        0.901,
        "Diamond markers indicate interpolated one-second crossing points between sample rows.",
        color=TEXT_MUTED,
        fontsize=9.5,
    )
    fig.legend(
        legend_handles,
        legend_labels,
        loc="lower center",
        ncol=4,
        frameon=True,
        framealpha=0.96,
        bbox_to_anchor=(0.5, 0.01),
    )
    fig.tight_layout(rect=[0, 0.22, 1, 0.88])
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
    gap = 0.9
    y_positions = list(range(len(ordered_video))) + [
        len(ordered_video) + gap + index for index in range(len(ordered_custom))
    ]

    labels = [STYLE[algorithm][0] for algorithm in ordered]
    values = [max(1.0, float(reaches[algorithm]["estimate"])) for algorithm in ordered]
    colors = [STYLE[algorithm][1] for algorithm in ordered]
    best_algorithm = max(reaches, key=lambda key: float(reaches[key]["estimate"]))
    baseline = reaches.get(LOCAL_BASELINE)

    fig, ax = plt.subplots(figsize=(12.8, 7.3))
    bars = ax.barh(y_positions, values, color=colors, edgecolor="#f8fafc", linewidth=0.9)
    for bar, algorithm in zip(bars, ordered):
        if algorithm_group(algorithm) == "video":
            bar.set_alpha(0.8)
            bar.set_hatch("//")
        else:
            bar.set_alpha(0.98)
        if algorithm == best_algorithm:
            bar.set_edgecolor("#0f172a")
            bar.set_linewidth(2.2)

    if ordered_video and ordered_custom:
        separator = len(ordered_video) - 0.45 + gap / 2
        ax.axhline(separator, color="#cbd5e1", linewidth=1.7)

    ax.axvline(VIDEO_TARGET_N, color="#ef4444", linestyle="--", linewidth=1.7)
    ax.set_xscale("log")
    ax.set_xlim(left=max(1, min(values) * 0.65), right=max(VIDEO_TARGET_N * 1.8, max(values) * 1.45))
    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Estimated largest n at one second (log scale)")
    fig.suptitle("How far each local algorithm gets in one second", weight="bold", y=0.98)

    if ordered_video and ordered_custom:
        left_label_x = ax.get_xlim()[0] * 1.06
        ax.text(
            left_label_x,
            separator - 0.18,
            "Video-inspired baseline",
            color=GROUP_CONFIG["video"]["accent"],
            fontsize=9.6,
            va="top",
            ha="left",
            weight="bold",
        )
        ax.text(
            left_label_x,
            separator + 0.18,
            "My C++ variants",
            color=GROUP_CONFIG["custom"]["accent"],
            fontsize=9.6,
            va="bottom",
            ha="left",
            weight="bold",
        )

    if baseline is not None:
        gain = (float(reaches[best_algorithm]["estimate"]) / float(baseline["estimate"]) - 1.0) * 100.0
        fig.text(
            0.105,
            0.91,
            f"Same-run baseline is the wheel-30 segmented sieve; best is {gain:.1f}% higher than that local baseline.",
            color=TEXT_MUTED,
            fontsize=10,
        )
    ax.grid(True, axis="x", alpha=0.35)

    if ordered_video and ordered_custom:
        ax.text(
            VIDEO_TARGET_N * 1.03,
            separator + 0.25,
            "video target",
            color="#ef4444",
            fontsize=9,
            va="bottom",
        )

    for bar, value, algorithm in zip(bars, values, ordered):
        emphasis = "bold" if algorithm == best_algorithm else "normal"
        target_ratio = value / VIDEO_TARGET_N
        suffix = "  winner" if algorithm == best_algorithm else ""
        ax.text(
            value * 1.05,
            bar.get_y() + bar.get_height() / 2,
            f"{format_int(value)} ({target_ratio:.2f}x target){suffix}",
            va="center",
            color="#0f172a",
            fontsize=9.6,
            weight=emphasis,
        )

    fig.tight_layout(rect=[0, 0, 1, 0.89])
    fig.savefig(out, dpi=180)
    plt.close(fig)


def plot_prime_growth(rows: dict[str, list[dict[str, float]]], out: pathlib.Path) -> None:
    reaches = reach_by_algorithm(rows)
    chosen = max(reaches, key=lambda key: float(reaches[key]["estimate"]))
    data = rows[chosen]
    label = STYLE[chosen][0]

    fig, ax = plt.subplots(figsize=(11, 6.2))
    ax.set_facecolor("#f8fbff")
    ax.plot(
        [item["n"] + 1 for item in data],
        [item["prime"] for item in data],
        marker="o",
        linewidth=2.4,
        color="#f59e0b",
    )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Prime index n + 1 (log scale; code uses zero-indexed n)")
    ax.set_ylabel("prime(n)")
    ax.set_title(f"Prime growth curve for current winner: {label}", weight="bold")
    ax.grid(True, which="both", alpha=0.35)
    ax.text(
        0.02,
        0.95,
        "This chart follows the current winner; all series are available in the one-second reach plot.",
        transform=ax.transAxes,
        color=TEXT_MUTED,
        fontsize=9.5,
    )
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

    under = best["measured_under"]
    over = best["measured_over"]
    if under is None:
        under_text = "no under-one-second sample"
    else:
        under_text = f"`n = {format_int(under['n'])}` at `{under['seconds']:.6f}s`"

    lines = [
        "# Benchmark Summary",
        "",
        f"Video target: [One second to find the BILLIONth PRIME]({VIDEO_URL}) targets `n = 1,000,000,000`.",
        "",
        "All comparisons below are same-run. Exact prime-index values are hardware-relative; the meaningful claim is relative lift between algorithms measured together.",
        "",
        f"Local best: `{best_label}` reaches an estimated `n = {format_int(float(best['estimate']))}` at one second.",
        f"Measured under-one-second anchor: {under_text}.",
    ]
    if under is not None and over is not None:
        lines.append(
            f"Interpolation bracket: log-log interpolation between `n = {format_int(under['n'])}` at `{under['seconds']:.6f}s` and `n = {format_int(over['n'])}` at `{over['seconds']:.6f}s`."
        )
        lines.append(
            "Index note: benchmark rows use zero-indexed `n`; interpolation is performed on `n + 1` and converted back to zero-indexed `n`."
        )

    if baseline is not None:
        gain = (float(best["estimate"]) / float(baseline["estimate"]) - 1.0) * 100.0
        if video_ratio >= 100.0:
            video_line = (
                f"This run reaches `~{video_ratio:.2f}%` of the video's one-billion headline target at the estimated one-second crossing."
            )
        else:
            video_line = (
                f"This run reaches `~{video_ratio:.2f}%` of the video's one-billion headline target at the estimated one-second crossing."
            )
        lines.extend(
            [
                f"Best vs. pre-bitset wheel-30 baseline: `{gain:.1f}%` higher estimated one-second reach.",
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
        group = GROUP_NAMES[algorithm_group(algorithm)]
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
        group = GROUP_NAMES[algorithm_group(algorithm)]
        best_row = data[-1]
        lines.append(
            f"| {group} | {label} | `{best_row['n']:,}` | `{best_row['prime']:,}` | `{best_row['seconds']:.6f}` |"
        )

    with out.open("w", encoding="utf-8", newline="\n") as file:
        file.write("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot benchmark graphs")
    parser.add_argument("csv", nargs="?", type=pathlib.Path, default=DATA)
    parser.add_argument("-o", "--output", type=pathlib.Path, default=GRAPH_DIR)
    args = parser.parse_args()

    rows = read_rows(args.csv)
    validate_known_algorithms(rows)
    args.output.mkdir(parents=True, exist_ok=True)
    apply_recruiter_style()

    plot_story_scorecard(rows, args.output / "story_scorecard.png")
    plot_runtime(rows, args.output / "runtime_curves.png")
    plot_max_under(rows, args.output / "one_second_reach.png")
    plot_prime_growth(rows, args.output / "prime_growth.png")
    write_summary(rows, args.output / "summary.md")
    print(args.output)


if __name__ == "__main__":
    main()
