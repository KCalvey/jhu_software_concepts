import os
import sys
import json

import pytest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)

import clean


@pytest.mark.analysis
def test_clean_text():
    assert clean._clean_text(None) is None
    assert clean._clean_text("") is None
    assert clean._clean_text("  Hello   World  ") == "Hello World"
    assert clean._clean_text("<b>Hello</b>") == "Hello"
    assert clean._clean_text("Tom &amp; Jerry") == "Tom & Jerry"


@pytest.mark.analysis
def test_clean_data():
    records = [
        {
            "program": "  Computer   Science ",
            "university": "<b>Johns Hopkins University</b>",
            "comments": " Great &amp; exciting ",
            "raw_program": "Original Program"
        }
    ]

    result = clean.clean_data(records)

    assert len(result) == 1
    assert result[0]["program"] == "Computer Science"
    assert result[0]["university"] == "Johns Hopkins University"
    assert result[0]["comments"] == "Great & exciting"
    assert result[0]["raw_program"] == "Original Program"
    assert result[0]["standardized_program"] == "Computer Science"
    assert result[0]["standardized_university"] == "Johns Hopkins University"


@pytest.mark.analysis
def test_load_and_save_data(tmp_path, monkeypatch):
    input_file = tmp_path / "input.json"
    output_file = tmp_path / "output.json"

    sample_records = [
        {
            "program": "Data Science",
            "university": "Johns Hopkins University"
        }
    ]

    input_file.write_text(
        json.dumps(sample_records),
        encoding="utf-8"
    )

    monkeypatch.setattr(clean, "INPUT_FILE", str(input_file))
    monkeypatch.setattr(clean, "OUTPUT_FILE", str(output_file))

    loaded = clean.load_data()

    assert loaded == sample_records

    clean.save_data(loaded)

    saved = json.loads(output_file.read_text(encoding="utf-8"))

    assert saved == sample_records


@pytest.mark.analysis
def test_main(tmp_path, monkeypatch):
    input_file = tmp_path / "input.json"
    output_file = tmp_path / "output.json"

    sample_records = [
        {
            "program": "<b>Computer Science</b>",
            "university": " Johns Hopkins University ",
            "comments": " Great program "
        }
    ]

    input_file.write_text(
        json.dumps(sample_records),
        encoding="utf-8"
    )

    monkeypatch.setattr(clean, "INPUT_FILE", str(input_file))
    monkeypatch.setattr(clean, "OUTPUT_FILE", str(output_file))

    clean.main()

    assert output_file.exists()

    saved = json.loads(output_file.read_text(encoding="utf-8"))

    assert len(saved) == 1
    assert saved[0]["program"] == "Computer Science"