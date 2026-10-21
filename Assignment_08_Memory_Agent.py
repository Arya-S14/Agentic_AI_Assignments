"""
Memory Agent: stores and repeats the last user command (LangChain + Matplotlib)

Install:   pip install langchain-core matplotlib
Run:       python memory_agent.py                 (visual, step-by-step with Next button)
           python memory_agent.py --interactive   (type your own commands in the terminal)
           python memory_agent.py --no-gui        (terminal only, runs all iterations)
"""

import argparse
import textwrap
import warnings

warnings.filterwarnings("ignore")  # hide LangChain deprecation notices

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda

# ----------------------------------------------------------------------------
# 1. CONFIGURATION (initial values)
# ----------------------------------------------------------------------------
# Words/phrases that mean "do the previous command again".
REPEAT_TRIGGERS = {"repeat", "again", "repeat that", "do it again", "same again", "!!"}

# Scripted demo commands. Iteration 1 is a "repeat" on purpose, to show what
# happens when memory is still empty.
DEMO_COMMANDS = [
    "repeat",
    "open report.txt",
    "repeat",
    "send email to Raj",
    "again",
    "play music",
    "repeat that",
    "repeat",
]

COLORS = {
    "stored": "#4C78A8",    # blue  : new command stored in memory
    "repeated": "#54A24B",  # green : last command successfully repeated
    "empty": "#E45756",     # red   : repeat asked, but memory empty
}


def is_repeat(text: str) -> bool:
    return text.strip().lower() in REPEAT_TRIGGERS


# ----------------------------------------------------------------------------
# 2. THE MEMORY AGENT (LangChain)
# ----------------------------------------------------------------------------
class MemoryAgent:
    """
    Pipeline (LangChain Runnable chain):
        parse  ->  act  ->  commit
    Memory = LangChain InMemoryChatMessageHistory (starts empty).
    """

    def __init__(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # hide LangChain deprecation notice
            self.memory = InMemoryChatMessageHistory()  # initial memory: empty
        self.iteration = 0                           # initial counter: 0
        self.chain = (
            RunnableLambda(self._parse)
            | RunnableLambda(self._act)
            | RunnableLambda(self._commit)
        )

    # --- memory lookup ------------------------------------------------------
    def last_command(self):
        """Most recent real (non-repeat) command stored in memory, else None."""
        for msg in reversed(self.memory.messages):
            if isinstance(msg, HumanMessage) and not is_repeat(msg.content):
                return msg.content
        return None

    # --- chain steps --------------------------------------------------------
    def _parse(self, text: str) -> dict:
        self.iteration += 1
        return {
            "iteration": self.iteration,
            "user_input": text.strip(),
            "is_repeat": is_repeat(text),
            "memory_before": self.last_command(),
        }

    def _act(self, state: dict) -> dict:
        if state["is_repeat"]:
            if state["memory_before"]:
                state["status"] = "repeated"
                state["executed"] = state["memory_before"]
                state["response"] = f"Repeating last command: '{state['executed']}'"
            else:
                state["status"] = "empty"
                state["executed"] = None
                state["response"] = "Nothing to repeat yet - memory is empty."
        else:
            state["status"] = "stored"
            state["executed"] = state["user_input"]
            state["response"] = f"Executing and storing: '{state['executed']}'"
        return state

    def _commit(self, state: dict) -> dict:
        self.memory.add_user_message(state["user_input"])
        self.memory.add_ai_message(state["response"])
        state["memory_after"] = self.last_command()
        state["history_len"] = len(self.memory.messages)
        return state

    # --- public API ---------------------------------------------------------
    def run(self, text: str) -> dict:
        return self.chain.invoke(text)


# ----------------------------------------------------------------------------
# 3. TERMINAL OUTPUT
# ----------------------------------------------------------------------------
def print_iteration(rec: dict) -> None:
    print(f"\n--- Iteration {rec['iteration']} ---")
    print(f"  User input     : {rec['user_input']!r}")
    print(f"  Is repeat?     : {rec['is_repeat']}")
    print(f"  Memory before  : {rec['memory_before']!r}")
    print(f"  Agent output   : {rec['response']}")
    print(f"  Memory after   : {rec['memory_after']!r}")
    print(f"  Messages in memory: {rec['history_len']}")


def print_conclusion(agent: MemoryAgent, records: list) -> None:
    stored = sum(r["status"] == "stored" for r in records)
    repeated = sum(r["status"] == "repeated" for r in records)
    empty = sum(r["status"] == "empty" for r in records)
    print("\n" + "=" * 60)
    print("FINAL CONCLUSION")
    print("=" * 60)
    print(f"Total iterations          : {len(records)}")
    print(f"New commands stored       : {stored}")
    print(f"Successful repeats        : {repeated}")
    print(f"Failed repeats (empty)    : {empty}")
    print(f"Messages in LangChain mem : {len(agent.memory.messages)}")
    print(f"Last command in memory    : {agent.last_command()!r}")
    print("\nFull memory log:")
    for m in agent.memory.messages:
        who = "USER " if isinstance(m, HumanMessage) else "AGENT"
        print(f"  [{who}] {m.content}")
    print("=" * 60)
    print("Conclusion: the agent stores each new command and, whenever the user")
    print("says 'repeat' (or similar), it replays the last stored command.")
    print("=" * 60)


# ----------------------------------------------------------------------------
# 4. VISUALIZATION (Matplotlib + Next button)
# ----------------------------------------------------------------------------
def run_gui(agent: MemoryAgent, commands: list) -> list:
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    from matplotlib.widgets import Button

    records: list = []
    fig = plt.figure(figsize=(13, 7.5))
    fig.canvas.manager.set_window_title("Memory Agent - Step by Step")
    ax = fig.add_axes([0.02, 0.14, 0.96, 0.82])
    btn_ax = fig.add_axes([0.40, 0.03, 0.20, 0.07])
    button = Button(btn_ax, "Start >>", color="#dfe8f5", hovercolor="#b9cdea")
    state = {"concluded": False}

    def short(text, width=18):
        text = "None" if text is None else str(text)
        return "\n".join(textwrap.wrap(text, width)) or text

    def box(x, y, w, h, text, color, fs=10, alpha=0.25):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4",
                                    fc=color, ec=color, alpha=alpha, lw=1.5))
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4",
                                    fc="none", ec=color, lw=1.8))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)

    def arrow(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", lw=2, color="#444"))

    def setup(title):
        ax.clear()
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.axis("off")
        ax.set_title(title, fontsize=15, fontweight="bold", pad=10)

    def draw_initial():
        setup("Initial State (before any command)")
        box(30, 55, 40, 20, "Memory (LangChain\nInMemoryChatMessageHistory)\n\nlast command = None\nmessages = 0",
            "#888888", fs=11)
        ax.text(50, 35, f"{len(commands)} commands queued.\nClick 'Start' to run iteration 1.",
                ha="center", fontsize=12)

    def draw_iteration(rec):
        c = COLORS[rec["status"]]
        setup(f"Iteration {rec['iteration']} of {len(commands)}  -  {rec['status'].upper()}")

        # Row 1: pipeline flow
        labels = [
            f"1. User Input\n'{short(rec['user_input'], 16)}'",
            f"2. Parse\nrepeat command?\n{'YES' if rec['is_repeat'] else 'NO'}",
            f"3. Memory Lookup\nlast = {short(rec['memory_before'], 14)}",
            f"4. Agent Output\n{short(rec['response'], 22)}",
        ]
        xs = [2, 27, 52, 77]
        for x, lab in zip(xs, labels):
            box(x, 76, 19, 16, lab, c, fs=9)
        for x in xs[:-1]:
            arrow(x + 20.5, 84, x + 24.5, 84)

        # Row 2: memory before -> after
        ax.text(50, 68, "LangChain Memory: last stored command", ha="center",
                fontsize=11, fontweight="bold")
        box(12, 47, 30, 14, f"BEFORE\n{short(rec['memory_before'], 26)}", "#888888", fs=10)
        box(58, 47, 30, 14, f"AFTER\n{short(rec['memory_after'], 26)}", c, fs=10)
        arrow(44, 54, 56, 54)
        note = {"stored": "New command -> memory updated",
                "repeated": "Repeat -> memory unchanged, command replayed",
                "empty": "Repeat on empty memory -> nothing to replay"}[rec["status"]]
        ax.text(50, 41, note, ha="center", fontsize=10, style="italic")

        # Row 3: timeline of all iterations so far
        ax.text(2, 33, "History timeline (blue=stored, green=repeated, red=failed repeat)",
                fontsize=10, fontweight="bold")
        n = len(commands)
        w = 96 / n
        for i, r in enumerate(records):
            x = 2 + i * w
            col = COLORS[r["status"]]
            hl = 1.0 if r is rec else 0.35
            ax.add_patch(FancyBboxPatch((x + 0.3, 6), w - 1.2, 22,
                                        boxstyle="round,pad=0.2", fc=col, ec=col,
                                        alpha=hl))
            ax.text(x + w / 2 - 0.3, 17,
                    f"#{r['iteration']}\n{short(r['user_input'], 9)}",
                    ha="center", va="center", fontsize=8,
                    color="white" if r is rec else "black")

    def finish():
        if not state["concluded"]:
            state["concluded"] = True
            print_conclusion(agent, records)

    def on_click(_event):
        idx = len(records)
        if idx < len(commands):
            rec = agent.run(commands[idx])
            records.append(rec)
            print_iteration(rec)
            draw_iteration(rec)
            if len(records) == len(commands):
                button.label.set_text("Finish (close)")
                finish()
            else:
                button.label.set_text(f"Next Iteration >> ({len(records) + 1}/{len(commands)})")
        else:
            plt.close(fig)
        fig.canvas.draw_idle()

    button.on_clicked(on_click)
    draw_initial()
    plt.show()
    return records


# ----------------------------------------------------------------------------
# 5. MODES
# ----------------------------------------------------------------------------
def run_terminal_only(agent: MemoryAgent, commands: list) -> list:
    records = []
    for cmd in commands:
        rec = agent.run(cmd)
        records.append(rec)
        print_iteration(rec)
    print_conclusion(agent, records)
    return records


def run_interactive(agent: MemoryAgent) -> list:
    print("Type commands. Say 'repeat' / 'again' / '!!' to replay the last one. 'quit' to stop.")
    records = []
    while True:
        text = input("\nYou > ").strip()
        if text.lower() in {"quit", "exit"}:
            break
        if not text:
            continue
        rec = agent.run(text)
        records.append(rec)
        print(f"Agent > {rec['response']}")
    if records:
        print_conclusion(agent, records)
    return records


def main():
    parser = argparse.ArgumentParser(description="LangChain memory agent")
    parser.add_argument("--interactive", action="store_true", help="type your own commands")
    parser.add_argument("--no-gui", action="store_true", help="terminal only, no window")
    args = parser.parse_args()

    agent = MemoryAgent()
    if args.interactive:
        run_interactive(agent)
    elif args.no_gui:
        run_terminal_only(agent, DEMO_COMMANDS)
    else:
        records = run_gui(agent, DEMO_COMMANDS)
        # If the window was closed early, still show what happened so far.
        if records and len(records) < len(DEMO_COMMANDS):
            print("\n(Window closed before the last iteration.)")
            print_conclusion(agent, records)


if __name__ == "__main__":
    main()