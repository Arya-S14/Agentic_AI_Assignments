"""
Finite State Machine (FSM) Chatbot with GREETING, HELP and GOODBYE states.

Requirements : Python 3.8+  and  matplotlib   ->   pip install matplotlib
Run (demo)   : python fsm_chatbot.py            (scripted conversation, Next/Back buttons)
Run (live)   : python fsm_chatbot.py --chat     (you type messages, then replay with buttons)
Controls     : [Next] / [Back] buttons  OR  Right / Left arrow keys

How it works (short):
  1. The chatbot is a 5-tuple  M = (Q, Sigma, delta, q0, F)
        Q     = {START, GREETING, HELP, GOODBYE}   states
        Sigma = {greet, help, bye, other}          input classes
        delta = TRANSITIONS table                  (state, input) -> (next state, reply)
        q0    = START                              initial state
        F     = {GOODBYE}                          final (accepting) state
  2. Every user message is CLASSIFIED into one input symbol by keyword matching.
  3. Each iteration (= one message) the machine looks up delta(current, symbol),
     moves to the next state and prints the reply.
  4. It stops when the final state GOODBYE is reached.
  5. The design is verified: complete table, all states reachable, GOODBYE reachable.
"""

import argparse
import math
import re
import textwrap

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Arc
from matplotlib.widgets import Button

# ----------------------------------------------------------------------------
# 1. FSM DEFINITION  (edit these freely)
# ----------------------------------------------------------------------------
STATES = ["START", "GREETING", "HELP", "GOODBYE"]
INPUTS = ["greet", "help", "bye", "other"]
START_STATE = "START"
FINAL_STATES = {"GOODBYE"}

# Keyword lists used to CLASSIFY raw text into an input symbol.
# Priority when several match:  bye > help > greet > other
KEYWORDS = {
    "bye":   ["bye", "goodbye", "exit", "quit", "see you", "good night", "cya"],
    "help":  ["help", "assist", "support", "guide", "options", "commands", "what can you do"],
    "greet": ["hi", "hello", "hey", "hola", "namaste", "good morning", "good evening"],
}
PRIORITY = ["bye", "help", "greet"]

HELP_TEXT = "I can greet you, show this help, and say goodbye. Try 'hi', 'help' or 'bye'."
BYE_TEXT = "Goodbye! Have a great day."

# delta : (state, input symbol) -> (next state, bot reply)
TRANSITIONS = {
    ("START", "greet"):    ("GREETING", "Hello! I'm FSMBot. Type 'help' to see what I can do."),
    ("START", "help"):     ("HELP", HELP_TEXT),
    ("START", "bye"):      ("GOODBYE", BYE_TEXT),
    ("START", "other"):    ("START", "I didn't catch that. Say 'hello' to begin."),

    ("GREETING", "greet"): ("GREETING", "Hello again! Type 'help' for options."),
    ("GREETING", "help"):  ("HELP", HELP_TEXT),
    ("GREETING", "bye"):   ("GOODBYE", BYE_TEXT),
    ("GREETING", "other"): ("GREETING", "Sorry, I only know hello, help and bye."),

    ("HELP", "greet"):     ("GREETING", "Hi again! Anything else? Type 'help' or 'bye'."),
    ("HELP", "help"):      ("HELP", HELP_TEXT),
    ("HELP", "bye"):       ("GOODBYE", BYE_TEXT),
    ("HELP", "other"):     ("HELP", "That isn't a command. " + HELP_TEXT),
}

# Scripted conversation used by the demo (covers every kind of transition)
DEMO_MESSAGES = ["asdf", "hello", "what can you do?", "tell me more",
                 "hi again", "help me please", "ok bye"]

# Where each state is drawn on the XY plane
POS = {"START": (1.4, 3.6), "GREETING": (4.6, 6.0), "HELP": (4.6, 1.2), "GOODBYE": (7.8, 3.6)}


# ----------------------------------------------------------------------------
# 2. INPUT CLASSIFIER  (raw text -> input symbol)
# ----------------------------------------------------------------------------
def classify(text):
    """Return (symbol, matched_keyword). Whole-word / whole-phrase matching."""
    t = text.lower()
    for sym in PRIORITY:
        for kw in KEYWORDS[sym]:
            if re.search(r"\b" + re.escape(kw) + r"\b", t):
                return sym, kw
    return "other", None


# ----------------------------------------------------------------------------
# 3. THE MACHINE  (records every iteration)
# ----------------------------------------------------------------------------
class ChatbotFSM:
    def __init__(self):
        self.state = START_STATE
        self.history = []

    @property
    def done(self):
        return self.state in FINAL_STATES

    def step(self, text):
        sym, kw = classify(text)
        nxt, reply = TRANSITIONS[(self.state, sym)]
        rec = dict(n=len(self.history) + 1, text=text, sym=sym, kw=kw,
                   src=self.state, dst=nxt, reply=reply)
        self.history.append(rec)
        self.state = nxt
        return rec


def run_script(messages):
    fsm = ChatbotFSM()
    ignored = []
    for m in messages:
        if fsm.done:
            ignored.append(m)
            continue
        fsm.step(m)
    return fsm, ignored


# ----------------------------------------------------------------------------
# 4. DESIGN CHECKS
# ----------------------------------------------------------------------------
def design_checks():
    live = [s for s in STATES if s not in FINAL_STATES]
    complete = all((s, c) in TRANSITIONS for s in live for c in INPUTS)
    # forward reachability from START
    seen, todo = {START_STATE}, [START_STATE]
    while todo:
        cur = todo.pop()
        for c in INPUTS:
            if (cur, c) in TRANSITIONS:
                n = TRANSITIONS[(cur, c)][0]
                if n not in seen:
                    seen.add(n)
                    todo.append(n)
    all_reach = seen == set(STATES)
    # every live state can reach a final state
    def reaches_final(s):
        seen2, todo2 = {s}, [s]
        while todo2:
            cur = todo2.pop()
            if cur in FINAL_STATES:
                return True
            for c in INPUTS:
                if (cur, c) in TRANSITIONS:
                    n = TRANSITIONS[(cur, c)][0]
                    if n not in seen2:
                        seen2.add(n)
                        todo2.append(n)
        return False
    no_deadend = all(reaches_final(s) for s in live)
    return [("Transition table is complete (every non-final state x every input)", complete),
            ("Every state is reachable from START", all_reach),
            ("GOODBYE is reachable from every state (no dead ends)", no_deadend)]


# ----------------------------------------------------------------------------
# 5. TERMINAL OUTPUT
# ----------------------------------------------------------------------------
W = 92


def print_definition():
    print("=" * W)
    print("FINITE STATE MACHINE CHATBOT  -  GREETING / HELP / GOODBYE")
    print("=" * W)
    print(f"Q  (states)        : {', '.join(STATES)}")
    print(f"Sigma (inputs)     : {', '.join(INPUTS)}")
    print(f"q0 (initial state) : {START_STATE}")
    print(f"F  (final states)  : {', '.join(sorted(FINAL_STATES))}")
    print("\nInput classification keywords (priority: bye > help > greet > other):")
    for sym in PRIORITY:
        print(f"  {sym:<6}: {', '.join(KEYWORDS[sym])}")
    print("\nTransition function delta(state, input) -> next state")
    print(f"{'':<12}" + "".join(f"{c:>12}" for c in INPUTS))
    print("-" * (12 + 12 * len(INPUTS)))
    for s in STATES:
        row = "".join(f"{TRANSITIONS[(s, c)][0] if (s, c) in TRANSITIONS else '-':>12}" for c in INPUTS)
        print(f"{s:<12}{row}")
    print()


def print_checks():
    print("Design checks:")
    for name, ok in design_checks():
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print()


def print_iterations(fsm):
    for r in fsm.history:
        print(f"--- Iteration {r['n']} ---")
        print(f"State before  : {r['src']}")
        print(f"User says     : \"{r['text']}\"")
        why = f"matched keyword '{r['kw']}'" if r["kw"] else "no keyword matched"
        print(f"Classified as : {r['sym']}   ({why})")
        print(f"delta({r['src']}, {r['sym']}) = {r['dst']}")
        print(f"Bot replies   : {r['reply']}")
        print(f"State after   : {r['dst']}\n")


def print_conclusion(fsm, ignored):
    h = fsm.history
    path = [START_STATE] + [r["dst"] for r in h]
    print("=" * W)
    print("FINAL CONCLUSION")
    print("=" * W)
    print("State path        :", " -> ".join(path))
    print(f"Messages processed: {len(h)}")
    print(f"Final state       : {fsm.state}  "
          f"({'ACCEPTED - conversation ended normally' if fsm.done else 'NOT final - conversation incomplete'})")
    visits = {}
    for s in path:
        visits[s] = visits.get(s, 0) + 1
    print("Visits per state  :", ", ".join(f"{s}={visits.get(s, 0)}" for s in STATES))
    used = {}
    for r in h:
        key = (r["src"], r["sym"], r["dst"])
        used[key] = used.get(key, 0) + 1
    print("Transitions used  :")
    for (a, c, b), k in used.items():
        print(f"   {a:<9} --{c}--> {b:<9} x{k}")
    if ignored:
        print(f"Ignored (after GOODBYE): {ignored}")
    print("\nTranscript:")
    for r in h:
        print(f"  You: {r['text']}")
        print(f"  Bot: {r['reply']}")
    print("=" * W)


# ----------------------------------------------------------------------------
# 6. VISUALIZATION  (XY plane: states are nodes, the agent moves along arrows)
# ----------------------------------------------------------------------------
C_VISITED, C_CURRENT, C_UNVISITED = "#2e9e5b", "#f2b134", "#cfe3f7"
C_EDGE, C_TAKEN = "#9a9a9a", "#2e9e5b"
NR = 0.85  # node radius
LOOP_DIR = {"START": (-0.6, 0.8)}  # where a state's self-loop is drawn (dx, dy)


def edge_table():
    """(src, dst) -> list of input symbols, excluding nothing."""
    e = {}
    for (s, c), (d, _) in TRANSITIONS.items():
        e.setdefault((s, d), []).append(c)
    return e


EDGES = edge_table()


def bez(p0, p2, rad, t):
    """Point on matplotlib's arc3 curve between p0 and p2 at parameter t."""
    mx, my = (p0[0] + p2[0]) / 2, (p0[1] + p2[1]) / 2
    dx, dy = p2[0] - p0[0], p2[1] - p0[1]
    cx, cy = mx + rad * dy, my - rad * dx
    return ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * cx + t ** 2 * p2[0],
            (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * cy + t ** 2 * p2[1])


class Viewer:
    def __init__(self, fsm, ignored):
        self.fsm, self.ignored = fsm, ignored
        self.h = fsm.history
        self.idx = 0
        self.last = len(self.h) + 1  # 0 = start screen, 1..n = iterations, n+1 = conclusion
        self.fig = plt.figure(figsize=(14.5, 7.8))
        try:
            self.fig.canvas.manager.set_window_title("FSM Chatbot")
        except Exception:
            pass
        self.ax = self.fig.add_axes([0.03, 0.13, 0.58, 0.78])
        self.ax_chat = self.fig.add_axes([0.64, 0.50, 0.34, 0.41])
        self.ax_calc = self.fig.add_axes([0.64, 0.13, 0.34, 0.34])
        ax_back = self.fig.add_axes([0.58, 0.025, 0.1, 0.06])
        ax_next = self.fig.add_axes([0.70, 0.025, 0.14, 0.06])
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

    # ---- helpers ----
    def _self_loop(self, ax, s, color, lw, label, zorder):
        x, y = POS[s]
        cx = sum(p[0] for p in POS.values()) / len(POS)
        cy = sum(p[1] for p in POS.values()) / len(POS)
        vx, vy = LOOP_DIR.get(s, (x - cx, y - cy))
        n = (vx ** 2 + vy ** 2) ** 0.5 or 1
        ux, uy = vx / n, vy / n
        r = 0.5
        ccx, ccy = x + (NR + r * 0.55) * ux, y + (NR + r * 0.55) * uy
        base = math.degrees(math.atan2(-uy, -ux))
        t1, t2 = base + 35, base + 325
        ax.add_patch(Arc((ccx, ccy), 2 * r, 2 * r, theta1=t1, theta2=t2, color=color,
                         lw=lw, zorder=zorder))
        m = math
        ex, ey = ccx + r * m.cos(m.radians(t2)), ccy + r * m.sin(m.radians(t2))
        px, py = ccx + r * m.cos(m.radians(t2 - 14)), ccy + r * m.sin(m.radians(t2 - 14))
        ax.annotate("", xy=(ex, ey), xytext=(px, py), zorder=zorder,
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=16))
        lx, ly = ccx + (r + 0.32) * ux, ccy + (r + 0.32) * uy
        ax.text(lx, ly, label, fontsize=8.5, ha="center", va="center", zorder=6,
                bbox=dict(fc="white", ec="none", alpha=0.9, pad=1))

    def draw(self):
        ax = self.ax
        ax.clear()
        final = self.idx == self.last
        k = min(self.idx, len(self.h))          # number of iterations shown
        done_recs = self.h[:k]
        cur_rec = self.h[k - 1] if (1 <= self.idx <= len(self.h)) else None
        agent = done_recs[-1]["dst"] if done_recs else START_STATE
        visited = {START_STATE} | {r["dst"] for r in done_recs}
        taken = {(r["src"], r["dst"]) for r in done_recs}
        cur_edge = (cur_rec["src"], cur_rec["dst"]) if cur_rec else None

        ax.set_xlim(-0.8, 9.6)
        ax.set_ylim(-1.5, 8.3)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_facecolor("#fbfbfb")

        # nodes first (arrows clip against these circles)
        circles = {}
        for s in STATES:
            fc = C_CURRENT if s == agent else (C_VISITED if s in visited else C_UNVISITED)
            c = Circle(POS[s], NR, fc=fc, ec="black", lw=4 if s == agent else 2, zorder=4)
            ax.add_patch(c)
            circles[s] = c
            if s in FINAL_STATES:
                ax.add_patch(Circle(POS[s], NR - 0.14, fc="none", ec="black", lw=1.4, zorder=5))
            ax.text(POS[s][0], POS[s][1] + 0.18, s, ha="center", va="center", fontsize=10,
                    fontweight="bold", color="white" if (s in visited and s != agent) else "black",
                    zorder=6)
        # start arrow
        sx, sy = POS[START_STATE]
        d = NR * 0.7071
        ax.annotate("", xy=(sx - d, sy - d), xytext=(sx - d - 1.0, sy - d - 1.0), zorder=3,
                    arrowprops=dict(arrowstyle="-|>", color="black", lw=1.8, mutation_scale=16))
        ax.text(sx - d - 1.05, sy - d - 1.25, "start", fontsize=8, ha="center", va="top")

        # edges
        for (a, b), syms in EDGES.items():
            label = " / ".join(syms)
            is_cur, is_taken = (a, b) == cur_edge, (a, b) in taken
            color = C_CURRENT if is_cur else (C_TAKEN if is_taken else C_EDGE)
            lw = 4.2 if is_cur else (2.8 if is_taken else 1.2)
            z = 3 if is_cur else (2.5 if is_taken else 1)
            if a == b:
                self._self_loop(ax, a, color, lw, label, z)
                continue
            rad = 0.22 if (b, a) in EDGES else 0.0
            ax.annotate("", xy=POS[b], xytext=POS[a], zorder=z,
                        arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=20,
                                        connectionstyle=f"arc3,rad={rad}", patchA=circles[a],
                                        patchB=circles[b], shrinkA=0, shrinkB=0,
                                        ls="--" if is_cur else "-"))
            t = 0.30 if ((a, b) == ("START", "GOODBYE") or (b, a) in EDGES) else 0.5
            lx, ly = bez(POS[a], POS[b], rad, t)
            ax.text(lx, ly, label, fontsize=8.5, ha="center", va="center", zorder=6,
                    fontweight="bold" if is_cur else "normal",
                    bbox=dict(fc="white", ec="none", alpha=0.9, pad=1))

        # agent token
        ax.scatter(POS[agent][0], POS[agent][1] - 0.42, marker="*", s=380, color="white",
                   edgecolor="black", linewidth=1.2, zorder=8)

        ax.legend(handles=[
            Line2D([0], [0], marker="*", color="w", markeredgecolor="black", markersize=15,
                   label="Agent (current state)"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor=C_CURRENT, markeredgecolor="black",
                   markersize=11, label="Current state"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor=C_VISITED, markeredgecolor="black",
                   markersize=11, label="Visited state"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor=C_UNVISITED, markeredgecolor="black",
                   markersize=11, label="Not visited yet"),
            Line2D([0], [0], color=C_CURRENT, lw=3.5, ls="--", label="Transition this iteration"),
            Line2D([0], [0], color=C_TAKEN, lw=2.8, label="Transition already taken"),
            Line2D([0], [0], color=C_EDGE, lw=1.2, label="Possible transition (label = input)"),
        ], loc="lower right", fontsize=7.5)
        title = ("FINAL RESULT - full path of the agent" if final else
                 "Initial state - waiting for the first message" if self.idx == 0 else
                 f"Iteration {self.idx} of {len(self.h)}")
        ax.set_title(title, fontsize=14, fontweight="bold", pad=10)

        # ---- chat transcript ----
        cx = self.ax_chat
        cx.clear()
        cx.set_xticks([])
        cx.set_yticks([])
        cx.set_title("Conversation", fontsize=10, loc="left")
        lines = []
        for r in done_recs:
            lines += textwrap.wrap("You: " + r["text"], 54, subsequent_indent="     ") or ["You:"]
            lines += textwrap.wrap("Bot: " + r["reply"], 54, subsequent_indent="     ")
        if not lines:
            lines = ["(no messages yet - press Next)"]
        lines = lines[-14:]
        cx.text(0.02, 0.97, "\n".join(lines), va="top", ha="left", fontsize=8.8,
                family="monospace", transform=cx.transAxes)

        # ---- calculation / conclusion ----
        kx = self.ax_calc
        kx.clear()
        kx.set_xticks([])
        kx.set_yticks([])
        kx.set_title("Transition calculation" if not final else "Conclusion", fontsize=10, loc="left")
        if final:
            path = [START_STATE] + [r["dst"] for r in self.h]
            ok = self.fsm.done
            txt = ("Path:\n" + textwrap.fill(" -> ".join(path), 56, initial_indent="  ",
                                             subsequent_indent="  ") +
                   f"\n\nMessages processed : {len(self.h)}\n"
                   f"Final state        : {self.fsm.state}\n"
                   f"Accepted           : {'YES' if ok else 'NO'}\n"
                   f"Visited states     : {len({START_STATE} | {r['dst'] for r in self.h})}/{len(STATES)}\n"
                   f"Design checks      : {'all passed' if all(o for _, o in design_checks()) else 'FAILED'}")
        elif cur_rec is None:
            txt = (f"State = {START_STATE} (q0)\n\nPress Next to feed the first\nmessage into the machine.\n\n"
                   "Each Next = one iteration:\n  1 classify the text\n  2 look up delta(state, input)\n"
                   "  3 move to the next state\n  4 bot sends the reply")
        else:
            r = cur_rec
            why = f"keyword '{r['kw']}'" if r["kw"] else "no keyword"
            txt = (f"Step 1  State before : {r['src']}\n"
                   f"Step 2  User says    : \"{r['text']}\"\n"
                   f"Step 3  Classify     : {r['sym']}  ({why})\n"
                   f"Step 4  delta({r['src']}, {r['sym']})\n"
                   f"                     = {r['dst']}\n"
                   f"Step 5  Bot replies  :\n" +
                   textwrap.fill(r["reply"], 54, initial_indent="    ", subsequent_indent="    ") +
                   f"\nStep 6  State after  : {r['dst']}")
        kx.text(0.02, 0.97, txt, va="top", ha="left", fontsize=8.8, family="monospace",
                transform=kx.transAxes)

        self.b_back.ax.set_visible(self.idx > 0)
        self.b_next.label.set_text("Finished" if final else "Next >")
        self.fig.canvas.draw_idle()


# ----------------------------------------------------------------------------
# 7. MAIN
# ----------------------------------------------------------------------------
def live_chat():
    print("Live chat mode. Type messages; say 'bye' to finish (Ctrl+C / Ctrl+D also stops).\n")
    fsm = ChatbotFSM()
    while not fsm.done:
        try:
            text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        r = fsm.step(text)
        print(f"Bot: {r['reply']}   [{r['src']} -> {r['dst']}]")
    print()
    return fsm, []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chat", action="store_true", help="type your own messages")
    ap.add_argument("--no-gui", action="store_true", help="terminal only")
    args = ap.parse_args()

    print_definition()
    print_checks()
    if args.chat:
        fsm, ignored = live_chat()
        if not fsm.history:
            print("No messages entered.")
            return
    else:
        fsm, ignored = run_script(DEMO_MESSAGES)
    print_iterations(fsm)
    print_conclusion(fsm, ignored)
    if args.no_gui:
        return
    print("\nOpening visualization window... use Next / Back (or arrow keys).")
    viewer = Viewer(fsm, ignored)  # keep reference alive
    plt.show()
    return viewer


if __name__ == "__main__":
    main()