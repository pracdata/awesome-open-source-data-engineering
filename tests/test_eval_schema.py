"""Validate all evals.json files conform to the AgentSkills.io eval specification."""

from pathlib import Path

import orjson

SKILLS_DIR = Path(__file__).parent.parent / ".claude" / "skills"


class TestEvalSchema:
    def _find_eval_files(self) -> list[Path]:
        return sorted(SKILLS_DIR.glob("*/evals/evals.json"))

    def test_eval_files_exist(self):
        files = self._find_eval_files()
        assert len(files) >= 36, f"Expected at least 36 eval files, found {len(files)}"

    def test_each_eval_parses_as_json(self):
        for path in self._find_eval_files():
            data = orjson.loads(path.read_bytes())
            assert isinstance(data, dict), f"{path} is not a JSON object"

    def test_each_eval_has_required_fields(self):
        for path in self._find_eval_files():
            data = orjson.loads(path.read_bytes())
            assert "skill_name" in data, f"{path} missing skill_name"
            assert "evals" in data, f"{path} missing evals"
            assert isinstance(data["evals"], list), f"{path} evals is not a list"
            assert len(data["evals"]) >= 1, f"{path} has no eval cases"

    def test_each_eval_entry_has_required_fields(self):
        for path in self._find_eval_files():
            data = orjson.loads(path.read_bytes())
            for entry in data["evals"]:
                assert "id" in entry, f"{path} eval missing id"
                assert "prompt" in entry, f"{path} eval missing prompt"
                assert "expected_output" in entry, f"{path} eval missing expected_output"
                assert "assertions" in entry, f"{path} eval missing assertions"

    def test_eval_ids_unique_within_skill(self):
        for path in self._find_eval_files():
            data = orjson.loads(path.read_bytes())
            ids = [e["id"] for e in data["evals"]]
            assert len(ids) == len(set(ids)), f"{path} has duplicate eval IDs"

    def test_assertions_are_non_empty(self):
        for path in self._find_eval_files():
            data = orjson.loads(path.read_bytes())
            for entry in data["evals"]:
                for assertion in entry["assertions"]:
                    assert isinstance(assertion, str), f"{path} assertion is not a string"
                    assert len(assertion.strip()) > 0, f"{path} has empty assertion"

    def test_skill_name_matches_directory(self):
        for path in self._find_eval_files():
            data = orjson.loads(path.read_bytes())
            dir_name = path.parent.parent.name
            assert data["skill_name"] == dir_name, f"{path}: skill_name '{data['skill_name']}' != dir '{dir_name}'"

    def test_prompts_are_realistic_length(self):
        for path in self._find_eval_files():
            data = orjson.loads(path.read_bytes())
            for entry in data["evals"]:
                assert len(entry["prompt"]) >= 10, f"{path} eval {entry['id']} prompt too short"
                assert len(entry["prompt"]) <= 1000, f"{path} eval {entry['id']} prompt too long"
