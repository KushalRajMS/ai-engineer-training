import os
import json
from pathlib import Path

class OutputWriter:
    def file_version(self, output_dir: str, filename: str):
        try:
            path = Path(output_dir) / f"{filename}_summary.json"
            if not path.exists():
                return str(path)
            stem = path.stem
            suffix = path.suffix

            counter = 1
            while True:
                new_path = Path(output_dir) / f"{stem}_{counter}{suffix}"
                if not new_path.exists():
                    return str(new_path)
                counter += 1
        except OSError:
            return (Path(output_dir) / f"{filename}_summaryfile.json")

    def save_result(self, result: dict, output_dir: str) -> bool:
        try:
            os.makedirs(Path(output_dir), exist_ok = True)
            filename_val = result.get("filename", "Unknown")
            stem = Path(filename_val).stem
            file_path = Path(self.file_version(output_dir= output_dir, filename= stem))
            with open(file_path, "w") as file:
                json.dump(result, file, indent= 4)
            return True
        except PermissionError:
            return False

    def save_batch_results(self, results: list[dict], output_dir: str) -> list[bool]:
        report_list: list[bool] = []
        for result in results:
            try:
                success = self.save_result(result= result, output_dir= output_dir)
                report_list.append(success)
            except Exception:
                report_list.append(False)
        return report_list

    def build_batch_report(self, results: list[dict], success_list: list[bool]) -> dict:
        failed_files = []
        success_count = success_list.count(True)
        failure_count = success_list.count(False)
        for i, result in enumerate(results):
            if not success_list[i]:
                failed_files.append(result.get("filename", "Unknown"))
        return {
            "total": len(results),
            "succeeded": success_count,
            "failed": failure_count,
            "failed_files": failed_files
        }