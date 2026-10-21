"""
To-Do Manager Agent (LangChain + simple persistent state + Matplotlib demo)

Install:  pip install langchain-core matplotlib
Run:
    python todo_agent.py                 Real CLI to-do manager (saves to todos.json)
    python todo_agent.py --demo          Visual step-by-step demo with a Next button
    python todo_agent.py --demo --no-gui Terminal-only demo (all iterations)
    python todo_agent.py --file my.json  Use a different save file

Commands:
    add <text>        add a task            list              show tasks
    done <id>         mark task done        delete <id>       remove a task
    clear             remove done tasks     help / quit
"""

import argparse
import json
import os
import re
import textwrap

from langchain_core.runnables import RunnableLambda

# ----------------------------------------------------------------------------
# 1. CONFIGURATION (initial values)
# ----------------------------------------------------------------------------
DEFAULT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todos.json")

ALIASES = {
    "ls": "list", "show": "list",
    "complete": "done", "finish": "done", "check": "done",
    "rm": "delete", "remove": "delete", "del": "delete",
    "exit": "quit", "q": "quit", "?": "help",
}

# Scripted commands for the visual demo (covers success, info and error cases).
DEMO_COMMANDS = [
    "list",                       # empty state
    "add Buy milk",
    "add Finish assignment",
    "add Call mom",
    "list",
    "done 2",
    "delete 1",
    "done 9",                     # error: id does not exist
    "add Read LangChain docs",
    "clear",                      # remove completed tasks
]

COLORS = {
    "add": "#4C78A8",      # blue
    "done": "#54A24B",     # green
    "delete": "#F58518",   # orange
    "clear": "#B279A2",    # purple
    "list": "#888888",     # grey
    "help": "#888888",
    "quit": "#888888",
    "error": "#E45756",    # red
}

HELP_TEXT = (
    "Commands: add <text> | list | done <id> | delete <id> | clear | help | quit"
)


# ----------------------------------------------------------------------------
# 2. SIMPLE STATE
# ----------------------------------------------------------------------------
class TodoState:
    """State = list of tasks + next id counter. Optionally saved to JSON."""

    def __init__(self, path=None):
        self.path = path
        self.tasks = []      # initial: empty list
        self.next_id = 1     # initial: first task gets id 1
        if path and os.path.exists(path):
            self._load()

    def _load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.tasks = data.get("tasks", [])
            # Re-derive the counter from the data so ids never collide.
            self.next_id = data.get("next_id", 1)
            if self.tasks:
                self.next_id = max(self.next_id, max(t["id"] for t in self.tasks) + 1)
        except (OSError, ValueError):
            print(f"[!] Could not read {self.path}; starting with an empty list.")

    def save(self):
        if not self.path:
            return
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"tasks": self.tasks, "next_id": self.next_id}, f, indent=2)

    def snapshot(self):
        return [dict(t) for t in self.tasks]

    def find(self, task_id):
        return next((t for t in self.tasks if t["id"] == task_id), None)

    @property
    def pending(self):
        return sum(not t["done"] for t in self.tasks)

    @property
    def completed(self):
        return sum(t["done"] for t in self.tasks)


def format_tasks(tasks):
    if not tasks:
        return "  (no tasks)"
    return "\n".join(f"  [{'x' if t['done'] else ' '}] {t['id']}. {t['text']}" for t in tasks)


# ----------------------------------------------------------------------------
# 3. THE TO-DO AGENT (LangChain chain: parse -> execute -> commit)
# ----------------------------------------------------------------------------
class TodoAgent:
    def __init__(self, path=None):
        self.state = TodoState(path)
        self.iteration = 0
        self.chain = (
            RunnableLambda(self._parse)
            | RunnableLambda(self._execute)
            | RunnableLambda(self._commit)
        )

    # Step 1: text -> structured command
    def _parse(self, text: str) -> dict:
        self.iteration += 1
        text = text.strip()
        parts = text.split(None, 1)
        word = parts[0].lower() if parts else ""
        action = ALIASES.get(word, word)
        arg = parts[1].strip() if len(parts) > 1 else ""
        known = {"add", "list", "done", "delete", "clear", "help", "quit"}
        return {
            "iteration": self.iteration,
            "raw": text,
            "action": action if action in known else ("empty" if not word else "unknown"),
            "arg": arg,
        }

    # Step 2: run the command on the state
    def _execute(self, s: dict) -> dict:
        st = self.state
        s["before"] = st.snapshot()
        a, arg = s["action"], s["arg"]
        s["status"] = "ok"

        def need_id():
            if not re.fullmatch(r"\d+", arg):
                s["status"], s["message"] = "error", f"Usage: {a} <id>  (id must be a number)"
                return None
            task = st.find(int(arg))
            if task is None:
                s["status"], s["message"] = "error", f"No task with id {arg}."
            return task

        if a == "add":
            if not arg:
                s["status"], s["message"] = "error", "Usage: add <task text>"
            else:
                task = {"id": st.next_id, "text": arg, "done": False}
                st.tasks.append(task)
                st.next_id += 1
                s["message"] = f"Added #{task['id']}: '{arg}'"
        elif a == "list":
            s["status"] = "info"
            s["message"] = "Your tasks:\n" + format_tasks(st.tasks) if st.tasks else "No tasks yet."
        elif a == "done":
            task = need_id()
            if task is not None:
                if task["done"]:
                    s["status"], s["message"] = "info", f"#{task['id']} is already done."
                else:
                    task["done"] = True
                    s["message"] = f"Completed #{task['id']}: '{task['text']}'"
        elif a == "delete":
            task = need_id()
            if task is not None:
                st.tasks.remove(task)
                s["message"] = f"Deleted #{task['id']}: '{task['text']}'"
        elif a == "clear":
            removed = [t for t in st.tasks if t["done"]]
            st.tasks = [t for t in st.tasks if not t["done"]]
            if removed:
                s["message"] = f"Cleared {len(removed)} completed task(s)."
            else:
                s["status"], s["message"] = "info", "No completed tasks to clear."
        elif a == "help":
            s["status"], s["message"] = "info", HELP_TEXT
        elif a == "quit":
            s["status"], s["message"] = "info", "Goodbye!"
        elif a == "empty":
            s["status"], s["message"] = "info", "Type a command (or 'help')."
        else:
            s["status"] = "error"
            s["message"] = f"Unknown command '{s['raw'].split()[0]}'. {HELP_TEXT}"
        return s

    # Step 3: save state + record the result
    def _commit(self, s: dict) -> dict:
        st = self.state
        st.save()
        s["after"] = st.snapshot()
        s["pending"], s["done_count"], s["next_id"] = st.pending, st.completed, st.next_id
        s["color_key"] = "error" if s["status"] == "error" else s["action"]
        return s

    def run(self, text: str) -> dict:
        return self.chain.invoke(text)


# ----------------------------------------------------------------------------
# 4. TERMINAL OUTPUT
# ----------------------------------------------------------------------------
def print_iteration(rec):
    print(f"\n--- Iteration {rec['iteration']} ---")
    print(f"  Command      : {rec['raw']!r}")
    print(f"  Parsed       : action={rec['action']!r}, arg={rec['arg']!r}")
    print(f"  Status       : {rec['status'].upper()}")
    print(f"  Result       : {rec['message']}")
    print(f"  Tasks before : {len(rec['before'])}  ->  after: {len(rec['after'])}")
    print(f"  Pending/Done : {rec['pending']} / {rec['done_count']}")


def print_conclusion(agent, records):
    def count(action):
        return sum(r["action"] == action and r["status"] == "ok" for r in records)

    errors = sum(r["status"] == "error" for r in records)
    print("\n" + "=" * 60)
    print("FINAL CONCLUSION")
    print("=" * 60)
    print(f"Total commands processed : {len(records)}")
    print(f"Tasks added              : {count('add')}")
    print(f"Tasks completed          : {count('done')}")
    print(f"Tasks deleted            : {count('delete')}")
    print(f"'clear' operations       : {count('clear')}")
    print(f"Errors handled           : {errors}")
    print(f"Pending / Done now       : {agent.state.pending} / {agent.state.completed}")
    print(f"Next id counter          : {agent.state.next_id}")
    print("\nFinal task list:")
    print(format_tasks(agent.state.tasks))
    if agent.state.path:
        print(f"\nState saved to: {agent.state.path}")
    print("=" * 60)
    print("Conclusion: the agent parsed each command, updated its state")
    print("(task list + id counter), and handled bad input without crashing.")
    print("=" * 60)


# ----------------------------------------------------------------------------
# 5. VISUAL DEMO (Matplotlib + Next button)
# ----------------------------------------------------------------------------
def run_gui(agent, commands):
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    from matplotlib.widgets import Button

    records = []
    fig = plt.figure(figsize=(13, 7.5))
    fig.canvas.manager.set_window_title("To-Do Agent - Step by Step")
    ax = fig.add_axes([0.02, 0.14, 0.96, 0.82])
    button = Button(fig.add_axes([0.40, 0.03, 0.20, 0.07]), "Start >>",
                    color="#dfe8f5", hovercolor="#b9cdea")
    flags = {"concluded": False}

    def short(text, width=18):
        text = "None" if text is None else str(text)
        return "\n".join(textwrap.wrap(text, width, break_long_words=False)) or text

    def trunc(text, n=30):
        return text if len(text) <= n else text[: n - 1] + "…"

    def box(x, y, w, h, text, color, fs=10, alpha=0.2):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4",
                                    fc=color, ec=color, alpha=alpha, lw=1.5))
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4",
                                    fc="none", ec=color, lw=1.8))
        if text:
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

    def task_box(x, y, w, h, title, tasks, color):
        box(x, y, w, h, "", color)
        ax.text(x + 1.5, y + h - 3, f"{title} ({len(tasks)} tasks)", fontsize=10,
                fontweight="bold", va="center")
        shown = tasks if len(tasks) <= 5 else tasks[:4]
        for i, t in enumerate(shown):
            mark = "[x]" if t["done"] else "[ ]"
            ax.text(x + 1.5, y + h - 8 - i * 3.6,
                    f"{mark} {t['id']}. {trunc(t['text'])}", fontsize=9, va="center",
                    color="#2e7d32" if t["done"] else "black", family="monospace")
        if len(tasks) > 5:
            ax.text(x + 1.5, y + h - 8 - 4 * 3.6, f"... +{len(tasks) - 4} more",
                    fontsize=9, va="center", style="italic")
        if not tasks:
            ax.text(x + w / 2, y + h / 2 - 2, "(empty)", ha="center", fontsize=10,
                    style="italic", color="#777")

    def draw_initial():
        setup("Initial State (before any command)")
        task_box(30, 48, 40, 26, "STATE", [], "#888888")
        ax.text(50, 40, "tasks = []     next_id = 1", ha="center", fontsize=11,
                family="monospace")
        ax.text(50, 28, f"{len(commands)} commands queued.\nClick 'Start' to run iteration 1.",
                ha="center", fontsize=12)

    def draw_iteration(rec):
        c = COLORS[rec["color_key"]]
        setup(f"Iteration {rec['iteration']} of {len(commands)}  -  "
              f"{rec['action'].upper()}  ({rec['status'].upper()})")

        # Row 1: pipeline
        msg = rec["message"].split("\n")[0]
        labels = [
            f"1. User Input\n'{short(rec['raw'], 16)}'",
            f"2. Parse\naction={rec['action']}\narg='{short(rec['arg'], 10)}'",
            f"3. Execute\non state\n(next_id={rec['next_id']})",
            f"4. Result\n{short(msg, 22)}",
        ]
        xs = [2, 27, 52, 77]
        for x, lab in zip(xs, labels):
            box(x, 78, 19, 15, lab, c, fs=9)
        for x in xs[:-1]:
            arrow(x + 20.5, 85, x + 24.5, 85)

        # Row 2: state before -> after
        task_box(4, 42, 40, 26, "BEFORE", rec["before"], "#888888")
        task_box(56, 42, 40, 26, "AFTER", rec["after"], c)
        arrow(46, 55, 54, 55)
        ax.text(50, 36.5, f"Pending: {rec['pending']}   Done: {rec['done_count']}   "
                          f"next_id: {rec['next_id']}",
                ha="center", fontsize=10, style="italic")

        # Row 3: timeline
        ax.text(2, 31, "Command timeline  (blue=add, green=done, orange=delete, "
                       "purple=clear, grey=info, red=error)", fontsize=9, fontweight="bold")
        n = len(commands)
        w = 96 / n
        for i, r in enumerate(records):
            x = 2 + i * w
            col = COLORS[r["color_key"]]
            current = r is rec
            ax.add_patch(FancyBboxPatch((x + 0.3, 5), w - 1.2, 22, boxstyle="round,pad=0.2",
                                        fc=col, ec=col, alpha=1.0 if current else 0.35))
            ax.text(x + w / 2 - 0.3, 16, f"#{r['iteration']}\n{short(r['raw'], 10)}",
                    ha="center", va="center", fontsize=7.5,
                    color="white" if current else "black")

    def finish():
        if not flags["concluded"]:
            flags["concluded"] = True
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
# 6. MODES
# ----------------------------------------------------------------------------
def run_demo_terminal(agent, commands):
    records = []
    for cmd in commands:
        rec = agent.run(cmd)
        records.append(rec)
        print_iteration(rec)
    print_conclusion(agent, records)


def run_cli(agent):
    print("To-Do Manager Agent. " + HELP_TEXT)
    if agent.state.tasks:
        print("\nLoaded saved tasks:")
        print(format_tasks(agent.state.tasks))
    records = []
    while True:
        try:
            text = input("\ntodo> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        rec = agent.run(text)
        records.append(rec)
        print(rec["message"])
        if rec["action"] == "quit":
            break
    if records:
        print_conclusion(agent, records)


def main():
    ap = argparse.ArgumentParser(description="LangChain to-do manager agent")
    ap.add_argument("--demo", action="store_true", help="run the scripted visual demo")
    ap.add_argument("--no-gui", action="store_true", help="with --demo: terminal only")
    ap.add_argument("--file", default=DEFAULT_FILE, help="JSON save file for the CLI")
    args = ap.parse_args()

    if args.demo:
        agent = TodoAgent(path=None)  # demo never touches your saved list
        if args.no_gui:
            run_demo_terminal(agent, DEMO_COMMANDS)
        else:
            records = run_gui(agent, DEMO_COMMANDS)
            if records and len(records) < len(DEMO_COMMANDS):
                print("\n(Window closed before the last iteration.)")
                print_conclusion(agent, records)
    else:
        run_cli(TodoAgent(path=args.file))


if __name__ == "__main__":
    main()