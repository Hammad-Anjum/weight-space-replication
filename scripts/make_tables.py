"""Render the result tables as PNG images (for the README, conclusion.md and the X thread).

    .venv/bin/python scripts/make_tables.py        -> figures/*.png

Numbers are typed in from LOG.md and the run files; each table names its sources in its footnote.
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "figures")

# Ink and surface tokens from the reference palette (light mode).
SURFACE, INK, INK2, MUTED, RULE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e4e3df"
ACCENT, ACCENT_BG = "#2a78d6", "#eaf2fc"

for f in ("/System/Library/Fonts/HelveticaNeue.ttc", "/System/Library/Fonts/Helvetica.ttc"):
    if os.path.exists(f):
        font_manager.fontManager.addfont(f)
plt.rcParams["font.family"] = ["Helvetica Neue", "Helvetica", "DejaVu Sans"]


def table(name, title, subtitle, header, rows, widths, footnotes, highlight=(), bold_cells=(), aligns=None):
    """rows: list of lists of str. highlight: row indexes with a tinted background.
    bold_cells: (row, col) cells drawn bold in the accent colour."""
    W = 1600
    row_h, head_h, top, foot_line = 64, 58, 150, 30
    H = top + head_h + row_h * len(rows) + 40 + foot_line * len(footnotes) + 30
    fig = plt.figure(figsize=(W / 200, H / 200), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")
    L, R = 60, W - 60
    ax.text(L, 62, title, fontsize=17, fontweight="bold", color=INK, va="baseline")
    ax.text(L, 104, subtitle, fontsize=10.5, color=INK2, va="baseline")
    xs = [L]
    for w in widths:
        xs.append(xs[-1] + w * (R - L))
    aligns = aligns or ["left"] + ["right"] * (len(header) - 1)

    def cell_x(c):
        return xs[c] + 14 if aligns[c] == "left" else xs[c + 1] - 14

    y = top
    for c, h in enumerate(header):
        ax.text(cell_x(c), y + head_h / 2, h, fontsize=10, color=INK2, fontweight="bold", va="center",
                ha=aligns[c])
    y += head_h
    ax.plot([L, R], [y, y], color=INK2, lw=1.2)
    for r, row in enumerate(rows):
        if r in highlight:
            ax.add_patch(plt.Rectangle((L, y), R - L, row_h, color=ACCENT_BG, lw=0, zorder=0))
        for c, v in enumerate(row):
            strong = (r, c) in bold_cells
            ax.text(cell_x(c), y + row_h / 2, v, fontsize=11.5, va="center", ha=aligns[c],
                    color=ACCENT if strong else (INK if c == 0 else INK),
                    fontweight="bold" if strong else "normal")
        y += row_h
        ax.plot([L, R], [y, y], color=RULE, lw=0.8)
    y += 40
    for i, f in enumerate(footnotes):
        ax.text(L, y + i * foot_line, f, fontsize=9, color=MUTED, va="baseline")
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, name)
    fig.savefig(p, facecolor=SURFACE)
    plt.close(fig)
    print("wrote", p)


def main():
    table(
        "1_qwen_math.png",
        "Qwen3.5-0.8B math: thinking OFF gets 43% with no edit",
        "Accuracy, and the share of answers that ran out of tokens before they finished",
        ["Setup", "Token limit", "MATH-500", "Ran out of tokens", "Source"],
        [
            ["Base model, thinking ON", "32k", "7.9%", "93%", "Authors (500 × 4)"],
            ["Astra's edit, thinking ON", "32k", "48.1%", "33%", "Authors (500 × 4)"],
            ["Base model, thinking ON", "16k", "8%", "92%", "Ours (50 problems)"],
            ["Astra's edit, thinking ON", "16k", "22%", "76%", "Ours (50 problems)"],
            ["Random edit, same place and size", "16k", "8%", "94%", "Ours (50 problems)"],
            ["Base model, thinking OFF (default)", "8k", "43%", "44%", "Ours (100 problems)"],
        ],
        [0.33, 0.11, 0.12, 0.18, 0.26],
        ["Ours: Apple M5 Pro, MLX, the authors' sampling settings, 1 sample per problem. Expect about ±5–7 points.",
         "Random edit: Astra's 64 columns and edit size, with the edit direction replaced by a random one.",
         "Thinking OFF uses the authors' own non-thinking settings (temperature 0.7, top-p 0.8, presence penalty 1.5)."],
        highlight={5}, bold_cells={(1, 2), (3, 2), (5, 2)},
        aligns=["left", "right", "right", "right", "left"],
    )
    table(
        "2_authors_runs.png",
        "The authors' Qwen runs: 1 of 7 found the big fix",
        "All Qwen3.5-0.8B thinking-ON runs in the authors' own results file (exp8_math/eval/RESULTS_excerpt.md)",
        ["Run", "Forward passes", "MATH-500", "In the blog post?"],
        [
            ["Prompt v2", "0", "7.9% (no edit made)", "No"],
            ["Prompt v3", "5", "7.9% (no edit submitted)", "No"],
            ["Prompt v3", "10", "12.3%", "Yes"],
            ["Prompt v3", "25", "14.1%", "Yes"],
            ["Prompt v3", "50", "48.1%", "Yes (headline)"],
            ["Prompt v4", "10", "7.9% (no edit submitted)", "No"],
            ["Prompt v4", "25", "14.1%", "No"],
            ["openwsp rerun, same model (GPT-6 Astra)", "50", "12.9%", "Independent group"],
        ],
        [0.36, 0.14, 0.28, 0.22],
        ["Base model: 7.9%. The authors' code notes mention 50.8% and 55.5% on practice problems, in what appear to be",
         "thinking-OFF runs (exp8_math/code/profiles.py). The post reports only thinking ON."],
        highlight={4}, bold_cells={(4, 2)},
        aligns=["left", "right", "right", "left"],
    )
    table(
        "3_minatar_ladder.png",
        "Write a game network from scratch: only top models can",
        "MinAtar game score of a 600→32→32→6 network that each model wrote in one reply, with no tools and no training",
        ["Model (effort)", "Breakout", "Seaquest", "Asterix"],
        [
            ["PPO, trained 100M steps", "15.8", "5.6", "25.8"],
            ["PPO, trained 500M steps", "25.3", "88.9", "55.2"],
            ["GPT-6 Astra, authors (1 run)", "517.4", "53.1", "53.2"],
            ["GPT-6 Astra, ours (2 runs)", "430, 590", "10.1, 3.3", "52.9, 69.0"],
            ["Claude Opus 5.5 (xhigh)", "stopped*", "18.0", "49.0"],
            ["Claude Sonnet 5.5 (xhigh)", "stopped*", "5.4", "29.0"],
            ["GPT-6 Luna (xhigh, 3 runs)", "0.0, 1.7, 2.3", "1.0, 0.0, 0.5", "0.9, 1.5, 3.1"],
            ["Claude Haiku 5.5 (xhigh)", "0.5", "1.3", "3.3"],
        ],
        [0.40, 0.20, 0.20, 0.20],
        ["Score: mean over 1,000 episodes, actions sampled, sticky actions 0.1. PPO rows are the authors' published numbers.",
         "* A safety filter stopped the Claude Breakout runs at xhigh. They have no score, and we do not count them as 0.",
         "Claude models ran as fresh Claude Code subagents (different system prompt from the authors' setup). See LOG.md."],
        highlight={3}, bold_cells={(3, 1), (3, 3), (4, 3)},
    )
    table(
        "4_checks.png",
        "Checks we ran before trusting our own numbers",
        "Does our setup reproduce the authors' released files?",
        ["Check", "Authors", "Ours", "Result"],
        [
            ["Rebuild Astra's 3 Qwen edits from public weights", "3 hashes", "3 match", "Pass"],
            ["Read Astra's 3 MinAtar replies into weights", "3 networks", "identical", "Pass"],
            ["Score Astra's Breakout network", "517.4", "502.9", "Pass (−3%)"],
            ["Score Astra's Seaquest network", "53.1", "52.2", "Pass (−2%)"],
            ["Score Astra's Asterix network", "53.2", "54.2", "Pass (+2%)"],
        ],
        [0.55, 0.16, 0.14, 0.15],
        ["Scores: 1,000 episodes each, MinAtar 1.0.15. Weights: Qwen/Qwen3.5-0.8B at revision 2fc0636."],
    )


if __name__ == "__main__":
    main()
