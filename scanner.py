import subprocess
import json
import os
from pathlib import Path
from typing import List, Dict
from config import AnalyzerConfig

project_root = os.path.dirname(os.path.abspath(__file__))
rules_config = os.path.join(project_root, "..", "rules", "custom_rules.yml")

def find_swift_files(root_dir: str, ignored: List[str]) -> List[str]:
    swift_files = []
    root = Path(root_dir)
    for path in root.rglob("*.swift"):
        rel_path = path.relative_to(root)
        if not any(str(rel_path).startswith(ign) for ign in ignored):
            swift_files.append(str(path))
    return swift_files


def run_swiftlint(config: AnalyzerConfig, target_dir: str) -> List[Dict]:
    swift_files = find_swift_files(target_dir, config.ignored_paths)
    if not swift_files:
        print("⚠️ No Swift files found in the specified directory.")
        return []

    cmd = [
        config.swiftlint_path,
        "lint",
        "--config", rules_config,
        "--reporter", "json",
        "--path", target_dir
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        raw_json = result.stdout.strip()
        if not raw_json:
            return []

        findings = json.loads(raw_json)
        structured = []
        for item in findings:
            structured.append({
                "file": item.get("file", ""),
                "line": item.get("line", 0),
                "severity": item.get("severity", "Warning"),
                "rule_id": item.get("type", "").replace("custom:", ""),
                "message": item.get("reason", "")
            })
        return structured
    except json.JSONDecodeError:
        print("❌ Failed to parse SwiftLint JSON output.")
        return []
    except Exception as e:
        print(f"❌ SwiftLint execution failed: {e}")
        return []