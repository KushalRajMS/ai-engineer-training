import pytest
from ai_training.pipeline.file_loader import FileLoader

@pytest.fixture
def create_folder_and_files(tmp_path):
    (tmp_path / "file1.txt").write_text("Hello!")
    (tmp_path / "file2.txt").write_text("Hello World!")
    (tmp_path / "file3.txt").write_bytes(b"\xff\xfe\x00\x01")
    (tmp_path / "file4.txt").write_text("")
    (tmp_path / "file5.csv").write_text("csv file")

    return tmp_path

def test_list_text_files(create_folder_and_files):
    file_loader = FileLoader()

    file_list = file_loader.list_text_files(directory_path= str(create_folder_and_files))
    assert len(file_list) == 4

    result = file_loader.list_text_files(directory_path="")
    assert result == []

    result = file_loader.list_text_files(directory_path= "kmc/file/doc")
    assert result == []

def test_read_file_content(create_folder_and_files):
    file_loader = FileLoader()
    file_list = file_loader.list_text_files(directory_path= str(create_folder_and_files))

    result = file_loader.read_file_content(file_path= file_list[0])
    assert result == "Hello!"

def test_load_text_files(create_folder_and_files):
    file_loader = FileLoader()

    result = file_loader.load_text_files(directory_path="")
    assert result == []

    result = file_loader.load_text_files(directory_path= str(create_folder_and_files))

    assert "filename" in result[1]
    assert result[0]["content"] == "Hello!"
    assert len(result) == 3