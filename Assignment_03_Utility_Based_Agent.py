"""
Utility-Based Agent: choose resources to maximize total score under a budget.

Requirements : Python 3.8+  and  matplotlib   ->   pip install matplotlib
Run          : python utility_agent.py
Controls     : [Next] / [Back] buttons  OR  Right / Left arrow keys

How it works (short):
  1. Every resource has 4 attributes: benefit, cost, time, reliability.
  2. Attributes are normalized to 0..1 (min-max) so they are comparable.
  3. Utility U = 100 * (wB*Bn + wR*R + wC*(1-Cn) + wT*(1-Tn))
  4. Each iteration the agent: finds affordable resources -> picks the one with
     the highest utility PER UNIT COST (best value for budget) -> pays its cost
     -> adds its utility to total score.
  5. Stops when nothing affordable is left.
  6. Result is compared against the brute-force optimal subset.
"""

import textwrap
from itertools import combinations

import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.lines import Line2D

# ----------------------------------------------------------------------------
# 1. PROBLEM DATA  (edit these freely)
# ----------------------------------------------------------------------------
BUDGET = 100

# name, benefit (0-100), cost (budget units), time (hours), reliability (0-1)
RESOURCES = [
    ("GPU Server",          90, 45,  6, 0.90),
    ("Data Engineer",       75, 30,  8, 0.85),
    ("Cloud Storage",       40, 10,  2, 0.95),
    ("Annotation Team",     65, 25,  9, 0.70),
    ("Monitoring Tool",     35, 12,  3, 0.90),
    ("Pretrained Model API", 80, 35,  4, 0.80),
    ("Security Audit",      50, 20,  7, 0.75),
    ("Training Course",     30, 15, 10, 0.60),
]

# Utility weights (must sum to 1.0)
W_BENEFIT, W_RELIABILITY, W_COST, W_TIME = 0.45, 0.25, 0.20, 0.10

# Pick rule:  "density" = highest utility / cost  (budget-aware, recommended)
#             "utility" = highest raw utility      (naive, shown for comparison)
STRATEGY = "density"

# ----------------------------------------------------------------------------
# 2. INITIAL VALUE CALCULATION  (normalization + utility)
# ----------------------------------------------------------------------------
NAMES = [r[0] for r in RESOURCES]
BEN = [r[1] for r in RESOURCES]
COST = [r[2] for r in RESOURCES]
TIME = [r[3] for r in RESOURCES]
REL = [r[4] for r in RESOURCES]
N = len(RESOURCES)


def minmax(values):
    lo, hi = min(values), max(values)
    return [(v - lo) / (hi - lo) if hi != lo else 0.0 for v in values]


BN, CN, TN = minmax(BEN), minmax(COST), minmax(TIME)


def utility(i):
    return 100 * (W_BENEFIT * BN[i] + W_RELIABILITY * REL[i]
                  + W_COST * (1 - CN[i]) + W_TIME * (1 - TN[i]))


UTIL = [utility(i) for i in range(N)]


def formula_text(i):
    """Human-readable step-by-step utility calculation for resource i."""
    a = W_BENEFIT * BN[i]
    b = W_RELIABILITY * REL[i]
    c = W_COST * (1 - CN[i])
    d = W_TIME * (1 - TN[i])
    return (
        f"U = 100*(wB*Bn + wR*R + wC*(1-Cn) + wT*(1-Tn))\n"
        f"  = 100*({W_BENEFIT}*{BN[i]:.3f} + {W_RELIABILITY}*{REL[i]:.2f}"
        f" + {W_COST}*{1 - CN[i]:.3f} + {W_TIME}*{1 - TN[i]:.3f})\n"
        f"  = 100*({a:.3f} + {b:.3f} + {c:.3f} + {d:.3f})\n"
        f"  = 100*{a + b + c + d:.4f} = {UTIL[i]:.2f}"
    )


# ----------------------------------------------------------------------------
# 3. THE AGENT  (greedy utility maximizer, records every iteration)
# ----------------------------------------------------------------------------
def score_key(i, strategy):
    return UTIL[i] / COST[i] if strategy == "density" else UTIL[i]


def run_agent(strategy=None):
    strategy = strategy or STRATEGY
    remaining = set(range(N))
    chosen = []
    budget = BUDGET
    total = 0.0
    steps = []
    it = 0
    while True:
        feasible = [i for i in remaining if COST[i] <= budget]
        status = {}
        for i in range(N):
            if i in chosen:
                status[i] = "selected"
            elif i in feasible:
                status[i] = "feasible"
            else:
                status[i] = "unaffordable" if i in remaining else "rejected"
        if not feasible:
            steps.append(dict(it=it + 1, budget_before=budget, budget_after=budget,
                              total=total, best=None, status=status,
                              chosen=list(chosen), feasible=[]))
            break
        it += 1
        best = max(feasible, key=lambda i: score_key(i, strategy))
        steps.append(dict(it=it, budget_before=budget, budget_after=budget - COST[best],
                          total=total + UTIL[best], best=best, status=status,
                          chosen=list(chosen), feasible=list(feasible)))
        budget -= COST[best]
        total += UTIL[best]
        chosen.append(best)
        remaining.remove(best)
    return steps, chosen, total, budget


def brute_force_optimal():
    best_set, best_score = (), 0.0
    for r in range(N + 1):
        for combo in combinations(range(N), r):
            if sum(COST[i] for i in combo) <= BUDGET:
                s = sum(UTIL[i] for i in combo)
                if s > best_score:
                    best_set, best_score = combo, s
    return best_set, best_score


# ----------------------------------------------------------------------------
# 4. TERMINAL OUTPUT
# ----------------------------------------------------------------------------
def print_setup():
    print("=" * 95)
    print("UTILITY-BASED AGENT  -  RESOURCE SELECTION")
    print("=" * 95)
    print(f"Budget = {BUDGET}")
    print(f"Weights: benefit={W_BENEFIT}, reliability={W_RELIABILITY}, "
          f"cost={W_COST}, time={W_TIME}\n")
    print(f"{'Resource':<22}{'Ben':>5}{'Cost':>6}{'Time':>6}{'Rel':>6}"
          f"{'Bn':>8}{'Cn':>8}{'Tn':>8}{'Utility':>10}{'U/Cost':>9}")
    print("-" * 95)
    for i in range(N):
        print(f"{NAMES[i]:<22}{BEN[i]:>5}{COST[i]:>6}{TIME[i]:>6}{REL[i]:>6.2f}"
              f"{BN[i]:>8.3f}{CN[i]:>8.3f}{TN[i]:>8.3f}{UTIL[i]:>10.2f}{UTIL[i] / COST[i]:>9.3f}")
    print(f"\nPick rule: {'highest utility per cost (U/Cost)' if STRATEGY == 'density' else 'highest raw utility'}\n")


def print_iterations(steps):
    for s in steps:
        if s["best"] is None:
            print(f"--- Stop: no remaining resource fits in budget {s['budget_before']} ---\n")
            continue
        b = s["best"]
        print(f"--- Iteration {s['it']} ---")
        print(f"Budget available : {s['budget_before']}")
        cands = sorted(s["feasible"], key=lambda i: -score_key(i, STRATEGY))
        print("Affordable (U, U/Cost): " + ", ".join(
            f"{NAMES[i]}({UTIL[i]:.2f}, {UTIL[i] / COST[i]:.2f})" for i in cands))
        skipped = [NAMES[i] for i, st in s["status"].items() if st == "unaffordable"]
        if skipped:
            print("Too expensive    : " + ", ".join(skipped))
        print(f"CHOSEN           : {NAMES[b]}  (utility {UTIL[b]:.2f}, cost {COST[b]}, "
              f"U/Cost {UTIL[b] / COST[b]:.3f})")
        print(f"Budget left      : {s['budget_before']} - {COST[b]} = {s['budget_after']}")
        print(f"Total score      : {s['total']:.2f}\n")


def print_conclusion(chosen, total, left):
    opt_set, opt_score = brute_force_optimal()
    print("=" * 95)
    print("FINAL CONCLUSION")
    print("=" * 95)
    print("Order of selection :", " -> ".join(NAMES[i] for i in chosen))
    print(f"Total cost spent   : {BUDGET - left} / {BUDGET}   (left = {left})")
    print(f"Total utility score: {total:.2f}")
    print("\nSanity check vs brute-force optimal subset:")
    print("  Optimal set      :", ", ".join(NAMES[i] for i in opt_set))
    print(f"  Optimal score    : {opt_score:.2f}")
    gap = opt_score - total
    if abs(gap) < 1e-9:
        print("  Result           : agent's greedy choice IS optimal.")
    else:
        print(f"  Result           : greedy is {gap:.2f} below optimal "
              f"({100 * total / opt_score:.1f}% of optimal).")
    if STRATEGY == "density":
        _, n_chosen, n_total, _ = run_agent("utility")
        print(f"\nFor comparison, naive 'highest raw utility' rule picks "
              f"{', '.join(NAMES[i] for i in n_chosen)} -> score {n_total:.2f}")
        print("  (it blows the budget on expensive items, so budget-aware U/Cost wins)")
    print("=" * 95)


# ----------------------------------------------------------------------------
# 5. VISUALIZATION  (XY plane: agent moves resource to resource; Next / Back buttons)
# ----------------------------------------------------------------------------
COLORS = {
    "selected": "#2e9e5b",      # green  - already bought
    "best": "#f2b134",          # gold   - picked this iteration
    "feasible": "#4a90d9",      # blue   - affordable candidate
    "unaffordable": "#d9534f",  # red    - cost > budget left
    "rejected": "#b0b0b0",      # grey   - not chosen (final screen)
}


def place_labels(xmax, ymax):
    """Greedy collision-avoiding label placement in data coordinates.
    Returns {i: (x, y, ha, va)}.  Works for any data you put in RESOURCES."""
    def box(x, y, ha, va, w, h):
        x0 = x if ha == "left" else x - w
        y0 = y if va == "bottom" else y - h
        return (x0, y0, x0 + w, y0 + h)

    def hit(a, b):
        return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])

    placed = [(COST[i] - 2.2, UTIL[i] - 4.5, COST[i] + 2.2, UTIL[i] + 4.5) for i in range(N)]
    placed.append((-1.5, -4, 6, 4))  # START marker
    out = {}
    for i in sorted(range(N), key=lambda k: -UTIL[k]):
        w = 0.50 * max(len(NAMES[i]), 18)
        h = 6.5
        x, y = COST[i], UTIL[i]
        cands = [(x + 2.6, y + 0.8, "left", "bottom"), (x - 2.6, y + 0.8, "right", "bottom"),
                 (x + 2.6, y - 0.8, "left", "top"), (x - 2.6, y - 0.8, "right", "top"),
                 (x, y + 5.2, "center", "bottom"), (x, y - 5.2, "center", "top")]
        chosen_c = cands[0]
        for c in cands:
            if c[2] == "center":
                b = (c[0] - w / 2, c[1] if c[3] == "bottom" else c[1] - h, c[0] + w / 2,
                     c[1] + h if c[3] == "bottom" else c[1])
            else:
                b = box(c[0], c[1], c[2], c[3], w, h)
            inside = b[0] >= -1.5 and b[2] <= xmax and b[1] >= -3 and b[3] <= ymax
            if inside and not any(hit(b, q) for q in placed):
                chosen_c = c
                placed.append(b)
                break
        else:
            placed.append(box(chosen_c[0], chosen_c[1], chosen_c[2], chosen_c[3], w, h))
        out[i] = chosen_c
    return out


class Viewer:
    def __init__(self, steps, chosen, total, left):
        self.steps, self.chosen, self.total, self.left = steps, chosen, total, left
        self.idx = 0
        self.last = len(steps)  # extra final "conclusion" screen
        self.fig = plt.figure(figsize=(14, 7.6))
        try:
            self.fig.canvas.manager.set_window_title("Utility-Based Agent")
        except Exception:
            pass
        gs = self.fig.add_gridspec(2, 2, width_ratios=[1.55, 1], height_ratios=[0.16, 0.84],
                                   left=0.07, right=0.98, top=0.90, bottom=0.13,
                                   hspace=0.18, wspace=0.12)
        self.ax_bar = self.fig.add_subplot(gs[:, 0])
        self.ax_budget = self.fig.add_subplot(gs[0, 1])
        self.ax_txt = self.fig.add_subplot(gs[1, 1])

        ax_back = self.fig.add_axes([0.58, 0.03, 0.1, 0.06])
        ax_next = self.fig.add_axes([0.70, 0.03, 0.14, 0.06])
        self.b_back = Button(ax_back, "< Back")
        self.b_next = Button(ax_next, "Next >", color="#cfe8ff", hovercolor="#9fd0ff")
        self.b_back.on_clicked(lambda e: self.go(-1))
        self.b_next.on_clicked(lambda e: self.go(+1))
        self.fig.canvas.mpl_connect(
            "key_press_event",
            lambda e: self.go(+1) if e.key == "right" else (self.go(-1) if e.key == "left" else None))
        self.draw()

    def go(self, d):
        self.idx = max(0, min(self.last, self.idx + d))
        self.draw()

    def draw(self):
        final = self.idx == self.last
        s = self.steps[min(self.idx, len(self.steps) - 1)]
        ax = self.ax_bar
        ax.clear()
        # ---- XY plane: x = Cost, y = Utility, agent starts at the origin ----
        XMAX, YMAX = 52, 88
        done = list(self.chosen) if final else list(s["chosen"])
        best = None if final else s["best"]
        pos_now = (COST[done[-1]], UTIL[done[-1]]) if done else (0, 0)

        # unaffordable zone: everything right of the remaining budget
        budget_now = self.left if final else s["budget_before"]
        if budget_now < XMAX:
            ax.axvspan(budget_now, XMAX, color=COLORS["unaffordable"], alpha=0.10, hatch="//")
            ax.axvline(budget_now, color=COLORS["unaffordable"], ls="--", lw=1.5)
            ax.text(budget_now + 0.6, YMAX - 3, f"budget left = {budget_now}\n(cost beyond this line is unaffordable)",
                    fontsize=8, color=COLORS["unaffordable"], va="top")

        # path travelled so far (numbered arrows between resources)
        prev = (0, 0)
        for k, i in enumerate(done):
            cur = (COST[i], UTIL[i])
            ax.annotate("", xy=cur, xytext=prev, zorder=2,
                        arrowprops=dict(arrowstyle="-|>", color=COLORS["selected"], lw=2.6,
                                        shrinkA=9, shrinkB=13, mutation_scale=18))
            prev = cur

        # this iteration: slope ray from origin + dashed move arrow to the pick
        if best is not None:
            bx_, by_ = COST[best], UTIL[best]
            k_ = by_ / bx_
            xe = min(XMAX, YMAX / k_)
            ax.plot([0, xe], [0, k_ * xe], ls=":", color="#888888", lw=1.2, zorder=1)
            ax.text(xe, k_ * xe, f"ray slope U/Cost = {k_:.2f}", fontsize=8, color="#444444",
                    ha="right" if xe > XMAX * 0.7 else "left", va="top",
                    bbox=dict(fc="white", ec="none", alpha=0.85, pad=1), zorder=1)
            ax.annotate("", xy=(bx_, by_), xytext=pos_now, zorder=3,
                        arrowprops=dict(arrowstyle="-|>", color=COLORS["best"], lw=3.2,
                                        ls="--", shrinkA=9, shrinkB=13, mutation_scale=20))

        # resource points
        labels = place_labels(XMAX, YMAX)
        for i in range(N):
            if final:
                st = "selected" if i in done else "rejected"
            elif i == best:
                st = "best"
            else:
                st = s["status"][i]
            ax.scatter(COST[i], UTIL[i], s=330, color=COLORS[st], edgecolor="black",
                       linewidth=1.3, zorder=4, hatch="//" if st == "unaffordable" else None)
            if i in done:
                ax.text(COST[i], UTIL[i], str(done.index(i) + 1), color="white", fontsize=10,
                        fontweight="bold", ha="center", va="center", zorder=5)
            elif i == best:
                ax.text(COST[i], UTIL[i], str(len(done) + 1), color="black", fontsize=10,
                        fontweight="bold", ha="center", va="center", zorder=5)
            lx, ly, lha, lva = labels[i]
            ax.text(lx, ly, f"{NAMES[i]}\n(cost {COST[i]}, U={UTIL[i]:.1f})",
                    fontsize=8, ha=lha, va=lva, zorder=5)

        # the agent and the start position
        ax.scatter(0, 0, marker="D", s=120, color="black", zorder=6)
        ax.text(0.8, 1.5, "START", fontsize=8, fontweight="bold")
        if not (final and not done):
            ax.scatter(*pos_now, marker="*", s=330, color="white", edgecolor="black",
                       linewidth=1.2, zorder=7)

        ax.set_xlim(-1.5, XMAX)
        ax.set_ylim(-3, YMAX)
        ax.set_xlabel("X  =  Cost (budget units)   -  moves right as it gets pricier")
        ax.set_ylabel("Y  =  Utility score   -  higher = better")
        ax.grid(alpha=0.3)
        ax.legend(handles=[
            Line2D([0], [0], marker="*", color="w", markeredgecolor="black", markersize=14,
                   label="Agent position"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor=COLORS["selected"],
                   markeredgecolor="black", markersize=11, label="Already selected (number = order)"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor=COLORS["best"],
                   markeredgecolor="black", markersize=11, label="Chosen this iteration"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor=COLORS["feasible"],
                   markeredgecolor="black", markersize=11, label="Affordable candidate"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor=COLORS["unaffordable"],
                   markeredgecolor="black", markersize=11, label="Too expensive now"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor=COLORS["rejected"],
                   markeredgecolor="black", markersize=11, label="Not selected"),
            Line2D([0], [0], color=COLORS["selected"], lw=2.6, label="Path travelled"),
            Line2D([0], [0], color=COLORS["best"], lw=3, ls="--", label="Move this iteration"),
        ], loc="lower right", fontsize=7.5)
        title = ("FINAL RESULT - full path of the agent" if final else
                 f"Iteration {s['it']} of {len(self.steps) - 1}" if s["best"] is not None
                 else "Agent stops - nothing affordable")
        ax.set_title(title, fontsize=14, fontweight="bold")

        # budget gauge
        bx = self.ax_budget
        bx.clear()
        spent_before = BUDGET - (self.left if final else s["budget_before"])
        bx.barh(0, BUDGET, color="#eeeeee", edgecolor="black")
        bx.barh(0, spent_before, color=COLORS["selected"], edgecolor="black")
        if not final and s["best"] is not None:
            bx.barh(0, COST[s["best"]], left=spent_before, color=COLORS["best"],
                    edgecolor="black")
        bx.set_xlim(0, BUDGET)
        bx.set_yticks([])
        left_now = self.left if final else s["budget_before"]
        bx.set_title(f"Budget: {BUDGET - left_now} spent, {left_now} left (of {BUDGET})",
                     fontsize=10)

        # text panel
        tx = self.ax_txt
        tx.clear()
        tx.axis("off")
        if final:
            opt_set, opt_score = brute_force_optimal()
            txt = ("CONCLUSION\n\n"
                   "Selected (in order):\n" +
                   "\n".join(f"  {k + 1}. {NAMES[i]}  (U={UTIL[i]:.2f}, cost {COST[i]})"
                             for k, i in enumerate(self.chosen)) +
                   f"\n\nTotal cost  : {BUDGET - self.left}/{BUDGET}\n"
                   f"Total score : {self.total:.2f}\n\n"
                   f"Brute-force optimum: {opt_score:.2f}\n" +
                   ("Greedy agent = optimal." if abs(opt_score - self.total) < 1e-9 else
                    f"Greedy reached {100 * self.total / opt_score:.1f}% of optimum."))
        elif s["best"] is None:
            txt = (f"No remaining resource costs <= {s['budget_before']}.\n\n"
                   f"Agent stops.\nTotal score so far: {s['total']:.2f}\n\n"
                   "Press Next for the conclusion.")
        else:
            b = s["best"]
            cands = sorted(s["feasible"], key=lambda i: -score_key(i, STRATEGY))
            rule = "U/Cost" if STRATEGY == "density" else "U"
            txt = (f"Step 1  Budget left = {s['budget_before']}\n"
                   f"Step 2  Affordable (cost <= {s['budget_before']}):\n" +
                   textwrap.fill(", ".join(NAMES[i] for i in cands), 46,
                                 initial_indent="    ", subsequent_indent="    ") + "\n"
                   f"Step 3  Pick max {rule} -> {NAMES[b]}\n"
                   f"        ({UTIL[b]:.2f}/{COST[b]} = {UTIL[b] / COST[b]:.3f})\n\n"
                   f"{formula_text(b)}\n\n"
                   f"Step 4  Budget: {s['budget_before']} - {COST[b]} = {s['budget_after']}\n"
                   f"Step 5  Total score: {s['total'] - UTIL[b]:.2f} + {UTIL[b]:.2f}"
                   f" = {s['total']:.2f}")
        tx.text(0, 1, txt, va="top", ha="left", fontsize=9, family="monospace",
                transform=tx.transAxes, wrap=True)

        self.b_back.ax.set_visible(self.idx > 0)
        self.b_next.label.set_text("Finished" if final else "Next >")
        self.fig.canvas.draw_idle()


# ----------------------------------------------------------------------------
# 6. MAIN
# ----------------------------------------------------------------------------
def main():
    assert abs(W_BENEFIT + W_RELIABILITY + W_COST + W_TIME - 1.0) < 1e-9, "weights must sum to 1"
    print_setup()
    steps, chosen, total, left = run_agent()
    print_iterations(steps)
    print_conclusion(chosen, total, left)
    print("\nOpening visualization window... use Next / Back (or arrow keys).")
    viewer = Viewer(steps, chosen, total, left)  # keep reference alive
    plt.show()
    return viewer


if __name__ == "__main__":
    main()