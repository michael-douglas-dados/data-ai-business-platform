"""Run all 20 cases in an isolated synthetic database and save evidence locally."""
import json
import os
import tempfile
from pathlib import Path
from app.cli import run_case

def main():
    root = Path(__file__).resolve().parents[1]
    projects = json.loads((root/"data/projects.json").read_text(encoding="utf-8"))
    report = []
    with tempfile.TemporaryDirectory() as directory:
        os.environ["WORKBENCH_DB"] = str(Path(directory)/"verification.db")
        for project in projects:
            result = run_case(project["id"])
            if result is None:
                raise AssertionError(project["id"])
            report.append({"project":project["id"],"status":"executed","result":result})
    target = root/"runtime"/"verification.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"{len(report)} cases executed. Evidence in runtime/verification.json")

if __name__ == "__main__":
    main()
