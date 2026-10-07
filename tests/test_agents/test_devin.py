from __future__ import annotations

from secfoo.agents import ADAPTERS, get_adapter
from secfoo.agents.devin import DevinAdapter


def test_registered_under_devin_id():
    assert ADAPTERS["devin"] is DevinAdapter
    assert isinstance(get_adapter("devin"), DevinAdapter)


def test_build_command_is_non_interactive_print_mode(tmp_path):
    cmd = DevinAdapter().build_command("hello", workdir=tmp_path)
    assert cmd[0] == "devin"
    assert cmd[cmd.index("-p") + 1] == "hello"


def test_build_command_disables_workspace_trust_check(tmp_path):
    # Required: devin's own docs say non-interactive mode fails in a
    # directory it hasn't seen before unless this is explicitly disabled.
    cmd = DevinAdapter().build_command("hello", workdir=tmp_path)
    assert cmd[cmd.index("--respect-workspace-trust") + 1] == "false"


def test_build_command_does_not_grant_edit_or_dangerous_permissions(tmp_path):
    cmd = DevinAdapter().build_command("hello", workdir=tmp_path)
    assert cmd[cmd.index("--permission-mode") + 1] == "auto"
    assert "accept-edits" not in cmd
    assert "dangerous" not in cmd


def test_extract_report_is_stdout_passthrough():
    # No JSON/output-format flag exists for devin (see module docstring),
    # so the default base-class behavior (stdout is the report) applies.
    assert DevinAdapter().extract_report("final report text") == "final report text"
