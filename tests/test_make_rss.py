"""一時停止中のRSS生成経路の回帰テスト。"""

import importlib
import runpy
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "make_rss.py"
BITFAN_URL = "https://ij-matome.bitfan.id/updates"
BITFAN_OUTPUT = "docs/ij_matome_updates_rss.xml"


@pytest.fixture
def generate_rss(monkeypatch):
    # The Actions job executes make_rss.py from the repository root.
    monkeypatch.syspath_prepend(str(SCRIPT.parent))
    return importlib.import_module("src.rss_maker.generate_rss")


def test_paused_jfn_does_not_block_bitfan(monkeypatch, capsys, generate_rss):
    calls = []

    def generate_bitfan(url, output):
        calls.append((url, output))

    def unexpected_jfn(*_args):
        pytest.fail("JFN Pods should not be contacted while paused")

    monkeypatch.setattr(
        generate_rss, "create_bitfan_updates_rss_file", generate_bitfan
    )
    monkeypatch.setattr(
        generate_rss, "create_jfn_pods_rss_file", unexpected_jfn
    )

    runpy.run_path(str(SCRIPT), run_name="__main__")

    assert calls == [(BITFAN_URL, BITFAN_OUTPUT)]
    assert "JFN Pods RSS更新は一時停止中" in capsys.readouterr().out


def test_bitfan_failure_still_exits_with_error(monkeypatch, generate_rss):
    def fail_bitfan(*_args):
        raise RuntimeError("Bitfan unavailable")

    def unexpected_jfn(*_args):
        pytest.fail("JFN Pods should not be contacted while paused")

    monkeypatch.setattr(
        generate_rss, "create_bitfan_updates_rss_file", fail_bitfan
    )
    monkeypatch.setattr(
        generate_rss, "create_jfn_pods_rss_file", unexpected_jfn
    )

    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(str(SCRIPT), run_name="__main__")

    assert excinfo.value.code == 1
