"""
Assignment 05 - Random-Walk Agent on a Grid

Problem statement : Program a random-walk agent that moves in a grid until it
                    reaches a target.

Requirements : Python 3.8+  and  matplotlib (numpy comes with it)
               ->   pip install matplotlib
Run          : python Assignment_05_Random_Walk_Agent.py
Options      : --seed 7      different random walk
               --size 6      grid is 6 x 6 (start bottom-left, target top-right)
               --no-gui      terminal output only
Controls     : [Next] [Back] [+10] [Play/Pause] [End]  OR  Right / Left arrows, Space = play

How it works (short):
  1. Grid of SIZE x SIZE cells, coordinates (x, y), origin (0, 0) bottom-left.
  2. Agent starts at START and has 4 actions: UP, DOWN, LEFT, RIGHT.
  3. Each iteration it draws r = random() in [0, 1) and maps it to an action:
        r < 0.25 UP | r < 0.50 DOWN | r < 0.75 LEFT | otherwise RIGHT
     (every action has probability 1/4 - the agent has NO strategy and NO memory).
  4. If the move would leave the grid it bumps the wall and stays; the step still counts.
  5. It stops the moment its position equals TARGET.
  6. Result is checked against theory: the exact expected number of steps is found by
     solving a system of linear equations, and a Monte-Carlo simulation is compared too.
"""

import argparse
import random

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.widgets import Button

# ----------------------------------------------------------------------------
# 1. PROBLEM DATA  (edit these freely)
# ----------------------------------------------------------------------------
SIZE = 5
START = (0, 0)
TARGET = (SIZE - 1, SIZE - 1)
SEED = 17
MAX_STEPS = 20000           # safety cap so the program can never loop forever
MC_RUNS = 3000              # Monte-Carlo runs used for the sanity check

# name, (dx, dy) - each chosen with probability 1/len(ACTIONS)
ACTIONS = [("UP", (0, 1)), ("DOWN", (0, -1)), ("LEFT", (-1, 0)), ("RIGHT", (1, 0))]


def configure(size, seed):
    global SIZE, TARGET, SEED
    SIZE, TARGET, SEED = size, (size - 1, size - 1), seed


# ----------------------------------------------------------------------------
# 2. THE AGENT  (random walk, records every iteration)
# ----------------------------------------------------------------------------
def manhattan(p):
    return abs(p[0] - TARGET[0]) + abs(p[1] - TARGET[1])


def pick_action(r):
    """Map r in [0,1) to an action index: [0,.25)=UP, [.25,.5)=DOWN, ..."""
    return min(int(r * len(ACTIONS)), len(ACTIONS) - 1)


def try_move(pos, a):
    dx, dy = ACTIONS[a][1]
    att = (pos[0] + dx, pos[1] + dy)
    inside = 0 <= att[0] < SIZE and 0 <= att[1] < SIZE
    return att, inside


def run_walk(seed, record=True):
    rng = random.Random(seed)
    pos, recs, steps = START, [], 0
    while pos != TARGET and steps < MAX_STEPS:
        steps += 1
        r = rng.random()
        a = pick_action(r)
        att, inside = try_move(pos, a)
        new = att if inside else pos
        if record:
            recs.append(dict(n=steps, r=r, a=a, name=ACTIONS[a][0], src=pos, att=att,
                             inside=inside, dst=new, d_before=manhattan(pos),
                             d_after=manhattan(new), reached=new == TARGET))
        pos = new
    return steps, recs, pos == TARGET


# ----------------------------------------------------------------------------
# 3. THEORY + MONTE CARLO  (sanity check)
# ----------------------------------------------------------------------------
def expected_steps():
    """Exact E[steps] from START by solving  E(s) = 1 + sum_a 1/4 * E(next(s,a)),  E(TARGET)=0."""
    if START == TARGET:
        return 0.0
    cells = [(x, y) for x in range(SIZE) for y in range(SIZE) if (x, y) != TARGET]
    idx = {c: i for i, c in enumerate(cells)}
    A, b = np.eye(len(cells)), np.ones(len(cells))
    for c in cells:
        for a in range(len(ACTIONS)):
            q, inside = try_move(c, a)
            q = q if inside else c
            if q != TARGET:
                A[idx[c], idx[q]] -= 1.0 / len(ACTIONS)
    return float(np.linalg.solve(A, b)[idx[START]])


def monte_carlo(runs):
    total, reached = 0, 0
    for k in range(runs):
        s, _, ok = run_walk(10_000 + k, record=False)
        total += s
        reached += ok
    return total / runs, reached


# ----------------------------------------------------------------------------
# 4. STATS + CHECKS
# ----------------------------------------------------------------------------
def stats(recs):
    cells = {START} | {r["dst"] for r in recs}
    visits = {START: 1}
    for r in recs:
        visits[r["dst"]] = visits.get(r["dst"], 0) + 1
    dists = [manhattan(START)] + [r["d_after"] for r in recs]
    return dict(unique=len(cells), visits=visits, bumps=sum(not r["inside"] for r in recs),
                backward=sum(r["d_after"] > r["d_before"] for r in recs),
                forward=sum(r["d_after"] < r["d_before"] for r in recs),
                same=sum(r["d_after"] == r["d_before"] for r in recs),
                max_d=max(dists), dists=dists)


def walk_checks(recs, reached):
    inside_all = all(0 <= r["dst"][0] < SIZE and 0 <= r["dst"][1] < SIZE for r in recs)
    one_cell = all(abs(r["dst"][0] - r["src"][0]) + abs(r["dst"][1] - r["src"][1]) <= 1 for r in recs)
    chained = all(recs[i]["dst"] == recs[i + 1]["src"] for i in range(len(recs) - 1))
    stop_ok = all(r["dst"] != TARGET for r in recs[:-1])
    return [("Every position stays inside the grid", inside_all),
            ("Every step moves at most one cell", one_cell),
            ("Each step starts where the previous one ended", chained),
            ("Walk stops the first time the target is reached", stop_ok and reached),
            ]


# ----------------------------------------------------------------------------
# 5. TERMINAL OUTPUT
# ----------------------------------------------------------------------------
W = 96


def print_setup(e_theory):
    print("=" * W)
    print("RANDOM-WALK AGENT  -  GRID WORLD")
    print("=" * W)
    print(f"Grid size        : {SIZE} x {SIZE}   (x, y) from (0,0) bottom-left to ({SIZE - 1},{SIZE - 1}) top-right")
    print(f"Start / Target   : {START}  ->  {TARGET}")
    print(f"Random seed      : {SEED}   (same seed = same walk; change it for a new walk)")
    print("Action rule      : r = random() in [0,1)")
    for i, (name, (dx, dy)) in enumerate(ACTIONS):
        lo, hi = i / len(ACTIONS), (i + 1) / len(ACTIONS)
        print(f"                   {lo:.2f} <= r < {hi:.2f}  ->  {name:<5} (dx={dx:+d}, dy={dy:+d})")
    print("Wall rule        : move outside the grid = bump, agent stays, step still counts")
    print(f"Start distance   : |{START[0]}-{TARGET[0]}| + |{START[1]}-{TARGET[1]}| = {manhattan(START)}")
    print(f"Theory           : expected steps to reach target from start = {e_theory:.2f}\n")


def print_iterations(recs):
    print(f"{'Step':>4}  {'From':<8}{'r':>7}  {'Action':<7}{'Tries':<9}{'Result':<10}{'To':<8}{'Dist':>9}")
    print("-" * 71)
    for r in recs:
        res = "moved" if r["inside"] else "BUMP"
        print(f"{r['n']:>4}  {str(r['src']):<8}{r['r']:>7.4f}  {r['name']:<7}{str(r['att']):<9}"
              f"{res:<10}{str(r['dst']):<8}{r['d_before']:>4}->{r['d_after']:<3}")
    print()
    r = recs[0]
    print("Worked example (step 1):")
    print(f"  position before = {r['src']},  r = {r['r']:.4f}")
    lo, hi = r["a"] / len(ACTIONS), (r["a"] + 1) / len(ACTIONS)
    print(f"  {lo:.2f} <= {r['r']:.4f} < {hi:.2f}  ->  action {r['name']}")
    print(f"  attempted position = {r['src']} + {ACTIONS[r['a']][1]} = {r['att']}")
    print(f"  inside grid? {'yes -> move' if r['inside'] else 'no -> bump, stay'};  position after = {r['dst']}")
    print(f"  distance = |{r['dst'][0]}-{TARGET[0]}| + |{r['dst'][1]}-{TARGET[1]}| = {r['d_after']}\n")


def print_conclusion(steps, recs, reached, e_theory, mc_mean, mc_reached):
    st = stats(recs)
    print("=" * W)
    print("FINAL CONCLUSION")
    print("=" * W)
    print(f"Target reached     : {'YES' if reached else 'NO (hit MAX_STEPS cap)'}")
    print(f"Steps taken        : {steps}")
    print(f"Final position     : {recs[-1]['dst']}   (target = {TARGET})")
    print(f"Moves / bumps      : {steps - st['bumps']} moves, {st['bumps']} wall bumps")
    print(f"Closer / farther   : {st['forward']} steps got closer, {st['backward']} got farther, "
          f"{st['same']} no change in distance")
    print(f"Cells visited      : {st['unique']} of {SIZE * SIZE} distinct; "
          f"most visited cell = {max(st['visits'], key=st['visits'].get)} "
          f"({max(st['visits'].values())} times)")
    print(f"Farthest from goal : distance {st['max_d']}   (started at {manhattan(START)})")
    print(f"Efficiency         : shortest possible path = {manhattan(START)} steps; "
          f"the walk used {steps} ({steps / max(manhattan(START), 1):.1f}x)")
    print("\nSanity check vs theory:")
    print(f"  Exact expected steps (linear system) : {e_theory:.2f}")
    print(f"  Monte-Carlo mean over {MC_RUNS} walks      : {mc_mean:.2f}   "
          f"({mc_reached}/{MC_RUNS} reached the target)")
    print(f"  This run                             : {steps}   "
          f"({'shorter' if steps < e_theory else 'longer'} than average - a single walk varies a lot)")
    ok_mc = abs(mc_mean - e_theory) / e_theory < 0.10
    print(f"  Monte-Carlo within 10% of theory     : {'PASS' if ok_mc else 'FAIL'}")
    print("\nWalk checks:")
    for name, ok in walk_checks(recs, reached):
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print("=" * W)


# ----------------------------------------------------------------------------
# 6. VISUALIZATION  (grid = XY plane, agent hops cell to cell)
# ----------------------------------------------------------------------------
C_TARGET, C_START = "#f9d56e", "#cfe3f7"
C_PATH, C_CUR, C_BUMP = "#2e9e5b", "#f2b134", "#d9534f"
CMAP = plt.get_cmap("Blues")


class Viewer:
    def __init__(self, recs, reached, e_theory, mc_mean):
        self.recs, self.reached, self.e_theory, self.mc_mean = recs, reached, e_theory, mc_mean
        self.n = len(recs)
        self.st_all = stats(recs)
        self.idx = 0
        self.last = self.n + 1          # 0 = initial, 1..n = steps, n+1 = conclusion
        self.playing = False
        self.fig = plt.figure(figsize=(14.5, 7.8))
        try:
            self.fig.canvas.manager.set_window_title("Random-Walk Agent")
        except Exception:
            pass
        self.ax = self.fig.add_axes([0.03, 0.17, 0.58, 0.75])
        self.ax_info = self.fig.add_axes([0.64, 0.50, 0.34, 0.42])
        self.ax_chart = self.fig.add_axes([0.68, 0.19, 0.29, 0.24])

        def btn(x, w, label, color="0.85", hover="0.95"):
            return Button(self.fig.add_axes([x, 0.035, w, 0.06]), label, color=color, hovercolor=hover)
        self.b_back = btn(0.64, 0.062, "< Back")
        self.b_next = btn(0.71, 0.062, "Next >", "#cfe8ff", "#9fd0ff")
        self.b_ten = btn(0.78, 0.062, "+10")
        self.b_play = btn(0.85, 0.062, "Play")
        self.b_end = btn(0.92, 0.062, "End >>")
        self.b_back.on_clicked(lambda e: self.go(-1))
        self.b_next.on_clicked(lambda e: self.go(+1))
        self.b_ten.on_clicked(lambda e: self.go(+10))
        self.b_end.on_clicked(lambda e: self.jump(self.last))
        self.b_play.on_clicked(lambda e: self.toggle_play())
        self.fig.canvas.mpl_connect("key_press_event", self.on_key)
        try:
            self.timer = self.fig.canvas.new_timer(interval=350)
            self.timer.add_callback(self.tick)
        except Exception:
            self.timer = None
        self.draw()

    # ---- navigation ----
    def on_key(self, e):
        if e.key == "right":
            self.go(+1)
        elif e.key == "left":
            self.go(-1)
        elif e.key == " ":
            self.toggle_play()

    def go(self, d):
        self.jump(self.idx + d)

    def jump(self, i):
        self.idx = max(0, min(self.last, i))
        if self.idx == self.last:
            self.stop_play()
        self.draw()

    def toggle_play(self):
        if self.timer is None:
            return
        if self.playing:
            self.stop_play()
        else:
            if self.idx == self.last:
                self.idx = 0
            self.playing = True
            self.timer.start()
        self.draw()

    def stop_play(self):
        self.playing = False
        if self.timer is not None:
            self.timer.stop()

    def tick(self):
        if self.idx >= self.last:
            self.stop_play()
            self.draw()
        else:
            self.go(+1)

    # ---- drawing ----
    def draw(self):
        final = self.idx == self.last
        k = min(self.idx, self.n)
        shown = self.recs[:k]
        cur = self.recs[k - 1] if 1 <= self.idx <= self.n else None
        pos = shown[-1]["dst"] if shown else START
        st = stats(shown)
        visits = st["visits"] if shown else {START: 1}
        maxv = max(visits.values())

        ax = self.ax
        ax.clear()
        ax.set_xlim(-0.6, SIZE - 0.4)
        ax.set_ylim(-0.6, SIZE - 0.4)
        ax.set_aspect("equal")
        ax.set_xticks(range(SIZE))
        ax.set_yticks(range(SIZE))
        ax.set_xlabel("X")
        ax.set_ylabel("Y")

        # cells shaded by visit count
        for x in range(SIZE):
            for y in range(SIZE):
                v = visits.get((x, y), 0)
                fc = CMAP(0.12 + 0.55 * v / maxv) if v else "white"
                if (x, y) == TARGET:
                    fc = C_TARGET
                ax.add_patch(Rectangle((x - 0.5, y - 0.5), 1, 1, fc=fc, ec="#b5b5b5", lw=1, zorder=1))
                if v and (x, y) != TARGET:
                    ax.text(x + 0.40, y - 0.42, str(v), fontsize=8, ha="right", va="bottom",
                            color="#33506b", zorder=2)
        ax.text(START[0] - 0.42, START[1] + 0.42, "START", fontsize=8, fontweight="bold",
                ha="left", va="top", zorder=3)
        ax.text(TARGET[0] - 0.42, TARGET[1] + 0.42, "TARGET", fontsize=8, fontweight="bold",
                ha="left", va="top", zorder=3)
        ax.scatter(*TARGET, marker="X", s=0)  # keeps legend order simple

        # path so far, fading from old to new
        moved = [r for r in shown if r["inside"] and r is not cur]
        for j, r in enumerate(moved):
            a = 0.25 + 0.6 * (j + 1) / max(len(moved), 1)
            ax.plot([r["src"][0], r["dst"][0]], [r["src"][1], r["dst"][1]], color=C_PATH,
                    lw=2.6, alpha=a, zorder=4, solid_capstyle="round")
        # wall bumps (edge of the cell in the blocked direction)
        for r in shown:
            dx, dy = ACTIONS[r["a"]][1]
            if not r["inside"]:
                big = r is cur
                ax.scatter(r["src"][0] + 0.5 * dx, r["src"][1] + 0.5 * dy, marker="x",
                           s=170 if big else 55, color=C_BUMP, linewidth=3 if big else 1.6, zorder=6)
        # current move
        if cur is not None and cur["inside"]:
            ax.annotate("", xy=cur["dst"], xytext=cur["src"], zorder=7,
                        arrowprops=dict(arrowstyle="-|>", color=C_CUR, lw=3.6, ls="--",
                                        shrinkA=6, shrinkB=10, mutation_scale=22))
        elif cur is not None:
            ax.text(cur["src"][0], cur["src"][1] - 0.62, "BUMP - stays", color=C_BUMP,
                    fontsize=9, fontweight="bold", ha="center", va="center", zorder=8)

        # agent
        ax.scatter(*pos, marker="*", s=520, color="white", edgecolor="black", linewidth=1.4, zorder=9)
        ax.scatter(*START, marker="D", s=40, color="black", zorder=5)

        ax.legend(handles=[
            Line2D([0], [0], marker="*", color="w", markeredgecolor="black", markersize=15, label="Agent"),
            Line2D([0], [0], marker="s", color="w", markerfacecolor=C_TARGET, markeredgecolor="#888",
                   markersize=11, label="Target cell"),
            Line2D([0], [0], marker="s", color="w", markerfacecolor=CMAP(0.5), markeredgecolor="#888",
                   markersize=11, label="Visited (darker = more visits, number = count)"),
            Line2D([0], [0], color=C_PATH, lw=2.6, label="Path travelled"),
            Line2D([0], [0], color=C_CUR, lw=3.4, ls="--", label="Move this iteration"),
            Line2D([0], [0], marker="x", color="w", markeredgecolor=C_BUMP, markersize=9,
                   markeredgewidth=2, label="Wall bump"),
        ], loc="upper center", bbox_to_anchor=(0.5, -0.10), ncol=3, fontsize=7.5, frameon=False)
        title = (f"FINAL RESULT - target reached in {self.n} steps" if final else
                 "Initial state - agent at START" if self.idx == 0 else f"Step {self.idx} of {self.n}")
        ax.set_title(title, fontsize=14, fontweight="bold", pad=10)

        # ---- info panel ----
        ix = self.ax_info
        ix.clear()
        ix.set_xticks([])
        ix.set_yticks([])
        ix.set_title("Conclusion" if final else "Step calculation", fontsize=10, loc="left")
        if final:
            sa = self.st_all
            txt = (f"Target reached     : {'YES' if self.reached else 'NO'}\n"
                   f"Steps taken        : {self.n}\n"
                   f"Final position     : {self.recs[-1]['dst']}\n"
                   f"Moves / bumps      : {self.n - sa['bumps']} / {sa['bumps']}\n"
                   f"Closer/farther/same: {sa['forward']} / {sa['backward']} / {sa['same']}\n"
                   f"Distinct cells     : {sa['unique']} of {SIZE * SIZE}\n"
                   f"Shortest possible  : {manhattan(START)} steps\n\n"
                   f"Theory (expected)  : {self.e_theory:.1f} steps\n"
                   f"Monte-Carlo mean   : {self.mc_mean:.1f} steps\n"
                   f"This run           : {self.n} steps\n\n"
                   f"Random walk has no plan: it only\nreaches the target by chance, and a\n"
                   f"single run can be far from average.")
        elif cur is None:
            txt = (f"Start = {START}   Target = {TARGET}\n"
                   f"Start distance = |{START[0]}-{TARGET[0]}| + |{START[1]}-{TARGET[1]}| = {manhattan(START)}\n\n"
                   f"Each Next = one iteration:\n"
                   f"  1 draw r = random()\n"
                   f"  2 map r to an action\n"
                   f"       r<.25 UP   r<.50 DOWN\n"
                   f"       r<.75 LEFT otherwise RIGHT\n"
                   f"  3 attempted = position + (dx,dy)\n"
                   f"  4 inside grid? move : bump, stay\n"
                   f"  5 distance = |x-tx| + |y-ty|\n"
                   f"  6 stop if position == target\n\n"
                   f"Seed = {SEED}  (same seed = same walk)")
        else:
            r = cur
            lo, hi = r["a"] / len(ACTIONS), (r["a"] + 1) / len(ACTIONS)
            dx, dy = ACTIONS[r["a"]][1]
            txt = (f"Step 1  Position before : {r['src']}\n"
                   f"Step 2  Draw r          : {r['r']:.4f}\n"
                   f"Step 3  {lo:.2f} <= r < {hi:.2f}\n"
                   f"        action = {r['name']}  (dx={dx:+d}, dy={dy:+d})\n"
                   f"Step 4  Attempted       : {r['src']} + ({dx:+d},{dy:+d})\n"
                   f"                        = {r['att']}\n"
                   f"Step 5  Inside grid?    : {'yes -> move' if r['inside'] else 'NO -> bump, stay'}\n"
                   f"        Position after  : {r['dst']}\n"
                   f"Step 6  Distance        : |{r['dst'][0]}-{TARGET[0]}| + |{r['dst'][1]}-{TARGET[1]}|\n"
                   f"                        = {r['d_after']}   (was {r['d_before']})\n"
                   f"Step 7  At target?      : {'YES - STOP' if r['reached'] else 'no, continue'}\n\n"
                   f"So far: {k} steps, {st['bumps']} bumps, {st['unique']} cells visited")
        ix.text(0.02, 0.97, txt, va="top", ha="left", fontsize=8.8, family="monospace",
                transform=ix.transAxes)

        # ---- distance chart ----
        cx = self.ax_chart
        cx.clear()
        d_all = self.st_all["dists"]
        d_now = d_all[:k + 1]
        cx.plot(range(len(d_now)), d_now, color="#4a90d9", lw=1.8, marker="o", ms=3)
        cx.scatter(len(d_now) - 1, d_now[-1], s=70, color=C_CUR, edgecolor="black", zorder=5)
        cx.set_xlim(0, max(self.n, 1))
        cx.set_ylim(-0.4, self.st_all["max_d"] + 0.8)
        cx.axhline(0, color=C_TARGET, lw=2, zorder=0)
        cx.set_xlabel("step", fontsize=8)
        cx.set_ylabel("distance to target", fontsize=8)
        cx.tick_params(labelsize=8)
        cx.grid(alpha=0.3)
        cx.set_title("Distance to target |x-tx| + |y-ty| (0 = reached)", fontsize=9, loc="left")

        self.b_back.ax.set_visible(self.idx > 0)
        self.b_next.label.set_text("Finished" if final else "Next >")
        self.b_play.label.set_text("Pause" if self.playing else "Play")
        self.fig.canvas.draw_idle()


# ----------------------------------------------------------------------------
# 7. MAIN
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--size", type=int, default=SIZE)
    ap.add_argument("--no-gui", action="store_true")
    args = ap.parse_args()
    configure(max(args.size, 2), args.seed)

    e_theory = expected_steps()
    print_setup(e_theory)
    steps, recs, reached = run_walk(SEED)
    if not recs:
        print("Start equals target - nothing to do.")
        return
    print_iterations(recs)
    mc_mean, mc_reached = monte_carlo(MC_RUNS)
    print_conclusion(steps, recs, reached, e_theory, mc_mean, mc_reached)
    if args.no_gui:
        return
    print("\nOpening visualization window... Next / Back / +10 / Play / End (or arrow keys, Space).")
    viewer = Viewer(recs, reached, e_theory, mc_mean)  # keep reference alive
    plt.show()
    return viewer


if __name__ == "__main__":
    main()