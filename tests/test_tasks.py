from __future__ import annotations

from pathlib import Path

from jarvis.assistant import Assistant
from jarvis.memory import MemoryStore, Task
from jarvis.tools import (
    ToolContext,
    add_task,
    clear_completed,
    complete_task,
    delete_task,
    tasks,
)


class TestTaskStore:
    def test_add_and_list(self, tmp_path: Path) -> None:
        store = MemoryStore(tmp_path / "mem.sqlite3")
        first = store.add_task("call the bank")
        second = store.add_task("buy milk")
        assert isinstance(first, Task)
        assert first.done is False
        items = store.list_tasks()
        assert len(items) == 2
        assert {item.body for item in items} == {"call the bank", "buy milk"}
        assert second.id > first.id

    def test_toggle(self, tmp_path: Path) -> None:
        store = MemoryStore(tmp_path / "mem.sqlite3")
        task = store.add_task("write report")
        toggled = store.toggle_task(task.id)
        assert toggled is not None and toggled.done is True
        assert store.toggle_task(task.id).done is False  # type: ignore[union-attr]
        assert store.toggle_task(9999) is None

    def test_delete_and_clear(self, tmp_path: Path) -> None:
        store = MemoryStore(tmp_path / "mem.sqlite3")
        one = store.add_task("one")
        two = store.add_task("two")
        store.toggle_task(one.id)
        assert store.clear_completed() == 1
        assert store.delete_task(two.id) is True
        assert store.delete_task(two.id) is False
        assert store.list_tasks() == []


class TestTaskTools:
    def test_add_task(self, tool_ctx: ToolContext) -> None:
        assert "Task #1 added" in add_task(tool_ctx, "email Sam")

    def test_empty_body(self, tool_ctx: ToolContext) -> None:
        assert "Tell me what to add" in add_task(tool_ctx, "  ")

    def test_empty_list(self, tool_ctx: ToolContext) -> None:
        assert "empty" in tasks(tool_ctx)

    def test_list_and_complete(self, tool_ctx: ToolContext) -> None:
        add_task(tool_ctx, "pay bills")
        listing = tasks(tool_ctx)
        assert "1 open" in listing
        assert "pay bills" in listing
        assert "now done" in complete_task(tool_ctx, "1")
        assert "0 open" in tasks(tool_ctx)
        assert "now open again" in complete_task(tool_ctx, "1")
        assert "Use `complete <task_id>`" in complete_task(tool_ctx, "abc")
        assert "No task found" in complete_task(tool_ctx, "999")

    def test_delete_and_clear(self, tool_ctx: ToolContext) -> None:
        add_task(tool_ctx, "a")
        add_task(tool_ctx, "b")
        complete_task(tool_ctx, "1")
        assert "Cleared 1" in clear_completed(tool_ctx)
        assert "Deleted task #2" in delete_task(tool_ctx, "2")
        assert "No task found" in delete_task(tool_ctx, "2")


class TestAssistantTaskRouting:
    def test_full_task_flow(self, tool_ctx: ToolContext) -> None:
        asst = Assistant(tool_ctx)
        assert "Task #1 added" in asst.handle("add task call the bank")
        assert "call the bank" in asst.handle("tasks")
        assert "now done" in asst.handle("complete 1")
        assert "0 open" in asst.handle("my tasks")
        assert "Cleared 1" in asst.handle("clear completed")
        assert "empty" in asst.handle("todo list")

    def test_task_prefixes(self, tool_ctx: ToolContext) -> None:
        asst = Assistant(tool_ctx)
        assert "Task #1 added" in asst.handle("todo buy milk")
        assert "Task #2 added" in asst.handle("new task book a flight")

    def test_greetings(self, tool_ctx: ToolContext) -> None:
        asst = Assistant(tool_ctx)
        assert "online and ready" in asst.handle("hello")
        assert "runs tasks for you" in asst.handle("who are you")
        assert "Anytime" in asst.handle("thanks")
