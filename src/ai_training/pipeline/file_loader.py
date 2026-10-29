from __future__ import annotations
from pathlib import Path

class FileLoader:
    def list_text_files(self, directory_path: str, extension: str = ".txt") -> list:
        files_list: list = []
        if not directory_path:
            return files_list
        dir_path = Path(directory_path)
        if not dir_path.exists():
            return files_list
        return list(sorted(dir_path.rglob(f"*{extension}"), key= lambda f: f.name))

    def read_file_content(self, file_path) -> str|None:
        try:
            filepath = Path(file_path)
            with open (filepath, "r") as f:
                content = f.read()
            return content
        except FileNotFoundError:
            print(f"{file_path} Not Found.")
            return None
        except PermissionError:
            print(f"{file_path} Access Denied.")
            return None
        except UnicodeDecodeError:
            print(f"Encoding Issue with File: {file_path}.")
            return None

    def load_text_files(self, directory_path: str, extension: str = ".txt") -> list[dict]:
        loaded_files: list[dict[str, str]] = []
        if not directory_path:
            return loaded_files
        file_list = self.list_text_files(directory_path= directory_path, extension= extension)
        if not file_list:
            return loaded_files
        
        for file in file_list:
            try:
                content = self.read_file_content(file_path= file)
                if content is None:
                    continue
                loaded_files.append({"filename": file.name, "content": content})
            except Exception:
                continue
        return loaded_files