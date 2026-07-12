"""TDD tests for MIST pc_control — complete but safe control of the host.

Verifies: capability gating, reversible file writes (backup+undo),
process listing, and honest provenance-tagged results.
"""
import os
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
from gateway.pc_control import PCControl, tag_pc


def test_read_only_inventory_needs_no_grant():
    ctl = PCControl()
    inv = ctl.inventory()
    assert "hostname" in inv and "os" in inv  # read-only is always allowed


def test_write_requires_capability_grant():
    ctl = PCControl()
    d = tempfile.mkdtemp()
    target = os.path.join(d, "x.txt")
    res = ctl.write_file(target, "hi", actor="test")
    assert res["ok"] is False
    assert res["reason"] == "capability 'fs.write' not granted"


def test_granted_write_is_reversible_with_backup():
    ctl = PCControl()
    ctl.grant("fs.write")
    d = tempfile.mkdtemp()
    target = os.path.join(d, "x.txt")
    res = ctl.write_file(target, "v1", actor="test")
    assert res["ok"] is True and res["provenance"].startswith("pc:")
    assert os.path.exists(target)
    # overwrite -> backup kept, undo restores previous content
    res2 = ctl.write_file(target, "v2", actor="test", backup=True)
    assert res2["ok"] is True
    assert os.path.getsize(res2["backup_of"]) >= 0  # backup file created
    undone = ctl.undo_last()
    assert undone is True
    assert open(target).read() == "v1"


def test_process_list_is_read_only():
    ctl = PCControl()
    procs = ctl.list_processes()
    assert isinstance(procs, list)  # may be empty if psutil absent; never errors


def test_grant_and_revoke():
    ctl = PCControl()
    ctl.grant("shell.exec")
    assert ctl.has_capability("shell.exec")
    ctl.revoke("shell.exec")
    assert not ctl.has_capability("shell.exec")


def test_result_is_provenance_tagged():
    sk = tag_pc("fs.write", True)
    assert sk["provenance"] == "pc:action"
    assert "actor" in sk
