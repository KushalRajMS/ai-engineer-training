from typer.testing import CliRunner
from ai_training.cli import app
from pathlib import Path
import json

runner = CliRunner()

def test_chat_runs_with_mock_provider():
    result = runner.invoke(app, ["bot", "--provider", "mock"], input="hello\nexit\n")
    assert result.exit_code == 0
    assert "Assistant:" in result.output

def test_chat_invalid_prompt_mode_shows_warning():
    result = runner.invoke(app, ["bot", "--provider", "mock", "--prompt-mode", "badmode"], input="exit\n")
    assert result.exit_code == 0
    assert "Unknown prompt mode" in result.output

def test_chat_unknow_provider():
    result = runner.invoke(app, ["bot", "--provider", "testprovider"], input="exit\n")
    assert result.exit_code == 1
    assert "Unknown provider" in result.output

def test_summarize_file_with_mock_provider(tmp_path):
    (tmp_path / "file1.txt").write_text("Hello My friend. I am doing good.")
    filepath = Path(tmp_path) / "file1.txt"
    result = runner.invoke(app, ["summarize-file", str(filepath), "--provider", "mock"])
    parsed_output = json.loads(result.output)
    assert result.exit_code == 0
    assert "My friend" in parsed_output["summary"]
    assert parsed_output["success"] == True
    assert parsed_output["filename"] == "file1.txt"

def test_batch_respone_output_dir(tmp_path):
    input_dir = tmp_path / "inputs"
    input_dir.mkdir()
    (input_dir / "file1.txt").write_text("Hello My friend. I am doing good.")
    output_dir = tmp_path / "output"
    result = runner.invoke(app, ["batch", str(input_dir), "--provider", "mock", "--output-dir", str(output_dir)])
    parsed_output = json.loads(result.output)
    assert result.exit_code == 0
    assert output_dir.exists() == True
    saved_files = list(output_dir.glob("*_summary.json"))
    assert len(saved_files) == 1
    assert "Mock response" in saved_files[0].read_text()
    assert "report" in parsed_output
    assert "results" in parsed_output
    assert parsed_output["report"]["total"] == 1

def test_ask_command(monkeypatch):
    monkeypatch.setattr(
        "ai_training.cli.build_retrieval_pipeline",
        lambda source, store, k: None
    )
    monkeypatch.setattr(
        "ai_training.cli.make_llm",
        lambda: None
    )
    monkeypatch.setattr(
        "ai_training.cli.run_rag_with_sources",
        lambda retriever, question, llm: {
            "answer": "AI is intelligence.",
            "sources": [{"source": "file.txt", "chunk_index": 0}]
        }
    )
    result = runner.invoke(app, ["ask", "What is AI?"])
    assert result.exit_code == 0
    assert "AI is intelligence." in result.output
    assert "file.txt" in result.output

def test_ingest_command(monkeypatch):
    monkeypatch.setattr("ai_training.cli.ingest_documents", lambda source: ["chunk1", "chunk2"])
    monkeypatch.setattr("ai_training.cli.make_embedder", lambda: None)
    monkeypatch.setattr("ai_training.cli.create_vector_store", lambda chunks, embedder: None)
    monkeypatch.setattr("ai_training.cli.save_vector_store", lambda vs, store: None)
    result = runner.invoke(app, ["ingest", "--source", "data/inputs/", "--store", "artifacts/vs/"])
    assert result.exit_code == 0
    assert "chunks" in result.output

def test_ask_missing_store(monkeypatch):
    monkeypatch.setattr(
        "ai_training.cli.load_vector_store",
        lambda store, embedder: (_ for _ in ()).throw(Exception("not found"))
    )
    monkeypatch.setattr("ai_training.cli.make_embedder", lambda: None)
    result = runner.invoke(app, ["ask", "What is AI?", "--store", "bad/path/"])
    assert result.exit_code == 0
    assert "not found" in result.output.lower() or "run" in result.output.lower()

def test_ask_empty_question():
    result = runner.invoke(app, ["ask", "", "--store", "artifacts/vector_store/"])
    assert result.exit_code == 0
    assert "empty" in result.output.lower() or "question" in result.output.lower()