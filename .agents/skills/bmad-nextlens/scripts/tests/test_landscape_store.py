from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys

import yaml


MODULE_PATH = Path(__file__).resolve().parent.parent / "landscape_store.py"
SPEC = importlib.util.spec_from_file_location("nextlens_landscape_store", MODULE_PATH)
LANDSCAPE_STORE = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = LANDSCAPE_STORE
SPEC.loader.exec_module(LANDSCAPE_STORE)


def test_initialize_landscape_dirs_creates_expected_structure(tmp_path: Path) -> None:
    directories = LANDSCAPE_STORE.initialize_landscape_dirs(tmp_path)

    assert set(directories) == set(LANDSCAPE_STORE.LANDSCAPE_ENTITY_DIRECTORIES)
    for directory_name in LANDSCAPE_STORE.LANDSCAPE_ENTITY_DIRECTORIES:
        assert (tmp_path / "landscape" / directory_name).is_dir()


def test_persist_landscape_entity_writes_parseable_entity_file(tmp_path: Path) -> None:
    entity = _entity_record()

    result = LANDSCAPE_STORE.persist_landscape_entity(tmp_path, entity)

    assert result.status == "pass"
    assert result.path == tmp_path / "landscape" / "role" / "role-system-architect.yaml"
    assert result.path is not None and result.path.exists()
    payload = yaml.safe_load(result.path.read_text(encoding="utf-8"))
    assert payload["identity"]["semanticId"] == "role-system-architect"
    assert payload["identity"]["opaqueId"] == "opaque-role-system-architect"
    assert payload["snapshot"]["title"] == "System Architect"
    assert payload["relationships"]["systemId"] == "system-nextlens"
    assert os.access(result.path, os.R_OK)
    assert os.access(result.path, os.W_OK)


def test_persist_landscape_entity_uses_atomic_replace(tmp_path: Path, monkeypatch) -> None:
    entity = _entity_record()
    replace_calls: list[tuple[Path, Path]] = []
    original_replace = LANDSCAPE_STORE.os.replace

    def recording_replace(src: str | os.PathLike[str], dst: str | os.PathLike[str]) -> None:
        replace_calls.append((Path(src), Path(dst)))
        original_replace(src, dst)

    monkeypatch.setattr(LANDSCAPE_STORE.os, "replace", recording_replace)

    result = LANDSCAPE_STORE.persist_landscape_entity(tmp_path, entity)

    assert result.status == "pass"
    assert any(src.suffix == ".tmp" and dst == result.path for src, dst in replace_calls)
    assert not any(path.suffix == ".tmp" for path in (tmp_path / "landscape" / "role").iterdir())


def test_persist_landscape_entity_rolls_back_on_write_failure(tmp_path: Path, monkeypatch) -> None:
    entity = _entity_record()
    existing_path = tmp_path / "landscape" / "role" / "role-system-architect.yaml"
    existing_path.parent.mkdir(parents=True, exist_ok=True)
    existing_path.write_text("original: true\n", encoding="utf-8")
    original_replace = LANDSCAPE_STORE.os.replace

    def failing_replace(src: str | os.PathLike[str], dst: str | os.PathLike[str]) -> None:
        src_path = Path(src)
        dst_path = Path(dst)
        if src_path.suffix == ".tmp" and dst_path == existing_path:
            raise PermissionError("write blocked")
        original_replace(src, dst)

    monkeypatch.setattr(LANDSCAPE_STORE.os, "replace", failing_replace)

    result = LANDSCAPE_STORE.persist_landscape_entity(tmp_path, entity)

    assert result.status == "fail"
    assert result.blocks_packet_emission is True
    assert result.rollback_performed is True
    assert result.error == "write blocked"
    assert existing_path.read_text(encoding="utf-8") == "original: true\n"


def _entity_record() -> LANDSCAPE_STORE.LandscapeEntityRecord:
    return LANDSCAPE_STORE.LandscapeEntityRecord(
        entity_type="role",
        semantic_id="role-system-architect",
        opaque_id="opaque-role-system-architect",
        name="System Architect",
        snapshot={"title": "System Architect", "status": "active"},
        relationships={"systemId": "system-nextlens"},
        metadata={"source": "context", "author": "operator"},
    )