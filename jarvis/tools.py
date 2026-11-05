from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import platform
import re
import shutil

from jarvis.llm import LlmClient
from jarvis.memory import MemoryStore
from jarvis.system_tasks import capabilities


@dataclass
class ToolContext:
    memory: MemoryStore
    llm: LlmClient


def help_text() -> str:
    return "\n".join(
        [
            "Commands:",
            "  help                         Show this help",
            "  capabilities                 Show the system tasks Jervis can perform",
            "  add task <thing>             Put something on your to-do list",
            "  tasks                        Show your to-do list",
            "  complete <task_id>           Tick a task off",
            "  delete task <task_id>        Remove a task",
            "  clear completed              Remove finished tasks",
            "  remember <text>              Save a note",
            "  notes                        List saved notes",
            "  forget <note_id>             Delete a note",
            "  remind me to <task> at <t>   Save a reminder",
            "  reminders                    List active reminders",
            "  done <reminder_id>           Mark a reminder done",
            "  status                       Show system status",
            "  chat <prompt>                Ask the optional AI assistant",
            "  exit                         Quit",
            "",
            capabilities(),
        ]
    )


def greeting() -> str:
    return (
        "Jervis here, online and ready. I can keep your to-do list, save notes and "
        "reminders, check the time and your files, or search the web. "
        "Type `help` for the full list, or just tell me something like "
        "`add task call the bank`."
    )


def identity() -> str:
    return (
        "I'm Jervis, a local assistant that runs tasks for you. Everything is stored "
        "in a small SQLite database on this computer, so your notes and tasks stay "
        "yours. Type `capabilities` to see what I can do."
    )


def thanks() -> str:
    return "Anytime. Say `tasks` when you want to see what's left to do."


def status() -> str:
    total, used, free = shutil.disk_usage(".")
    return "\n".join(
        [
            f"OS: {platform.system()} {platform.release()}",
            f"Machine: {platform.machine()}",
            f"Python: {platform.python_version()}",
            f"Disk free: {_bytes_to_gb(free)} GB / {_bytes_to_gb(total)} GB",
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ]
    )


def remember(ctx: ToolContext, body: str) -> str:
    if not body:
        return "Tell me what to remember."
    note = ctx.memory.add_note(body)
    return f"Remembered note #{note.id}."


def notes(ctx: ToolContext) -> str:
    saved = ctx.memory.list_notes()
    if not saved:
        return "No notes saved yet."
    return "\n".join(f"#{note.id}: {note.body} ({note.created_at})" for note in saved)


def forget(ctx: ToolContext, raw_id: str) -> str:
    try:
        note_id = int(raw_id.strip())
    except ValueError:
        return "Use `forget <note_id>`."
    if ctx.memory.delete_note(note_id):
        return f"Deleted note #{note_id}."
    return f"No note found with id #{note_id}."


def remind(ctx: ToolContext, command: str) -> str:
    match = re.match(r"remind me to (.+?) at (.+)$", command, flags=re.IGNORECASE)
    if not match:
        return "Use `remind me to <task> at <time>`."
    body = match.group(1).strip()
    remind_at = match.group(2).strip()
    reminder = ctx.memory.add_reminder(body, remind_at)
    return f"Reminder #{reminder.id} saved for {reminder.remind_at}."


def reminders(ctx: ToolContext) -> str:
    active = ctx.memory.list_reminders()
    if not active:
        return "No active reminders."
    return "\n".join(
        f"#{reminder.id}: {reminder.body} at {reminder.remind_at}"
        for reminder in active
    )


def done(ctx: ToolContext, raw_id: str) -> str:
    try:
        reminder_id = int(raw_id.strip())
    except ValueError:
        return "Use `done <reminder_id>`."
    if ctx.memory.mark_reminder_done(reminder_id):
        return f"Marked reminder #{reminder_id} done."
    return f"No reminder found with id #{reminder_id}."


# --------------------------------------------------------------------- tasks

def add_task(ctx: ToolContext, body: str) -> str:
    body = body.strip()
    if not body:
        return "Tell me what to add, for example `add task email the team`."
    task = ctx.memory.add_task(body)
    return f"Task #{task.id} added: {task.body}"


def tasks(ctx: ToolContext) -> str:
    items = ctx.memory.list_tasks()
    if not items:
        return "Your task list is empty. Add one with `add task <something>`."
    open_count = sum(1 for task in items if not task.done)
    done_count = len(items) - open_count
    lines = [f"Your tasks ({open_count} open, {done_count} done):"]
    for task in items:
        mark = "[x]" if task.done else "[ ]"
        lines.append(f"  {mark} #{task.id}: {task.body}")
    lines.append("Use `complete <id>` to tick one off, or `delete task <id>` to remove it.")
    return "\n".join(lines)


def complete_task(ctx: ToolContext, raw_id: str) -> str:
    try:
        task_id = int(raw_id.strip())
    except ValueError:
        return "Use `complete <task_id>`."
    task = ctx.memory.toggle_task(task_id)
    if task is None:
        return f"No task found with id #{task_id}."
    state = "done" if task.done else "open again"
    return f"Task #{task.id} ({task.body}) is now {state}."


def delete_task(ctx: ToolContext, raw_id: str) -> str:
    try:
        task_id = int(raw_id.strip())
    except ValueError:
        return "Use `delete task <task_id>`."
    if ctx.memory.delete_task(task_id):
        return f"Deleted task #{task_id}."
    return f"No task found with id #{task_id}."


def clear_completed(ctx: ToolContext) -> str:
    removed = ctx.memory.clear_completed()
    if removed == 0:
        return "No completed tasks to clear."
    return f"Cleared {removed} completed task(s)."


def chat(ctx: ToolContext, prompt: str) -> str:
    if not prompt:
        return "Use `chat <prompt>`."
    return ctx.llm.complete(prompt)


def _bytes_to_gb(value: int) -> str:
    return f"{value / 1024 / 1024 / 1024:.1f}"
