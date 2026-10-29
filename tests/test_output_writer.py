import pytest
import json
from pathlib import Path
from ai_training.pipeline.output_writer import OutputWriter

results = [
    {"filename": "file1.txt", "summary": "It is saying hello", "success": True},
    {"filename": "file2.txt", "summary": "It has many things about politics", "success": True},
    {"filename": "file3.txt", "summary": None, "success": False}
]

def test_save_batch_results(tmp_path):
    output_writer = OutputWriter()
    report_list = output_writer.save_batch_results(results= results, output_dir= str(tmp_path))
    assert report_list.count(True) == 3

    try:
        file_path = Path(tmp_path) / "file1_summary.json"
        with open(file_path, "r") as file:
            content = json.load(file)
        assert content == results[0]
    except FileNotFoundError:
        pytest.fail("FileNotFound")
    except PermissionError:
        pytest.fail("No Access to File")

    report = output_writer.build_batch_report(results= results, success_list= report_list)
    assert report["total"] == 3
    assert report["succeeded"] == 3
    assert report["failed"] == 0

def test_save_batch_results_new(tmp_path):
    output_writer = OutputWriter()
    folder_path = Path(tmp_path) / "new_folder"
    report_list = output_writer.save_batch_results(results= results, output_dir= str(folder_path))
    assert report_list.count(True) == 3

    try:
        file_path = folder_path / "file1_summary.json"
        with open(file_path, "r") as file:
            content = json.load(file)
        assert content == results[0]
    except FileNotFoundError:
        pytest.fail("FileNotFound")
    except PermissionError:
        pytest.fail("No Access to File")

def test_ssave_batch_results_with_one_failure(tmp_path, monkeypatch):
    output_writer = OutputWriter()
    real_open = open

    def fake_open(file, mode="r", *args, **kwargs):
        if "file2" in str(file) and mode == "w":
            raise PermissionError("Simulated permission error")
        return real_open(file, mode, *args, **kwargs)

    monkeypatch.setattr("builtins.open", fake_open)

    resport_lists = output_writer.save_batch_results(results= results, output_dir= str(tmp_path))

    assert resport_lists == [True, False, True]

    report = output_writer.build_batch_report(results= results, success_list= resport_lists)
    assert report["failed"] == 1
    assert "file2.txt" in report["failed_files"]