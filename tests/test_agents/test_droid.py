from __future__ import annotations

import json

from secfoo.agents import ADAPTERS, get_adapter
from secfoo.agents.droid import DroidAdapter


def test_registered_under_droid_id():
    assert ADAPTERS["droid"] is DroidAdapter
    assert isinstance(get_adapter("droid"), DroidAdapter)


def test_build_command_is_non_interactive_exec(tmp_path):
    cmd = DroidAdapter().build_command("hello", workdir=tmp_path)
    assert cmd[:2] == ["droid", "exec"]


def test_build_command_uses_json_output(tmp_path):
    cmd = DroidAdapter().build_command("hello", workdir=tmp_path)
    assert cmd[cmd.index("--output-format") + 1] == "json"


def test_build_command_sets_working_root(tmp_path):
    cmd = DroidAdapter().build_command("hello", workdir=tmp_path)
    assert cmd[cmd.index("--cwd") + 1] == str(tmp_path)


def test_build_command_does_not_grant_write_access(tmp_path):
    # `droid exec` defaults to read-only mode with no flag -- a review-only
    # skill must never pass --auto or --skip-permissions-unsafe.
    cmd = DroidAdapter().build_command("hello", workdir=tmp_path)
    assert "--auto" not in cmd
    assert "--skip-permissions-unsafe" not in cmd


def test_prompt_is_last_arg_after_double_dash(tmp_path):
    cmd = DroidAdapter().build_command("--looks-like-a-flag", workdir=tmp_path)
    assert cmd[-2:] == ["--", "--looks-like-a-flag"]


def test_extract_report_pulls_result_field():
    stdout = json.dumps({"result": "final report text", "usage": {}})
    assert DroidAdapter().extract_report(stdout) == "final report text"


def test_extract_report_falls_back_to_raw_stdout_on_bad_json():
    assert DroidAdapter().extract_report("not json") == "not json"


def test_extract_usage_sums_token_fields():
    stdout = json.dumps(
        {
            "result": "ok",
            "usage": {
                "input_tokens": 100,
                "cache_creation_input_tokens": 10,
                "cache_read_input_tokens": 5,
                "output_tokens": 50,
                "factory_credits": 3,
            },
        }
    )
    usage = DroidAdapter().extract_usage(stdout)
    assert usage.input_tokens == 115
    assert usage.output_tokens == 50
    # factory_credits is not a dollar figure -- must not be reported as cost.
    assert usage.cost_usd is None


def test_extract_usage_unknown_on_bad_json():
    usage = DroidAdapter().extract_usage("not json")
    assert usage.input_tokens is None
    assert usage.output_tokens is None
    assert usage.cost_usd is None
