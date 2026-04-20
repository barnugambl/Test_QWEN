import subprocess
import json
import os
import re
from pathlib import Path
from typing import List, Dict
from config import AnalyzerConfig


def find_swift_files(root_dir: str, ignored: List[str]) -> List[str]:
    """Находит все Swift файлы в директории, исключая указанные пути."""
    swift_files = []
    root = Path(root_dir)
    for path in root.rglob("*.swift"):
        rel_path = path.relative_to(root)
        if not any(str(rel_path).startswith(ign) for ign in ignored):
            swift_files.append(str(path))
    return swift_files


def load_custom_rules(rules_path: str) -> List[Dict]:
    """Загружает кастомные правила из YAML файла."""
    import yaml
    
    if not os.path.exists(rules_path):
        print(f"⚠️  Rules file not found: {rules_path}")
        return []
    
    with open(rules_path, 'r', encoding='utf-8') as f:
        rules_data = yaml.safe_load(f)
    
    # Преобразуем словарь правил в список
    rules = []
    if isinstance(rules_data, dict):
        for rule_id, rule_config in rules_data.items():
            rule = {
                'id': rule_id,
                'name': rule_config.get('name', rule_id),
                'regex': rule_config.get('regex', ''),
                'message': rule_config.get('message', ''),
                'severity': rule_config.get('severity', 'warning')
            }
            rules.append(rule)
    
    return rules


def analyze_file_with_rules(file_path: str, rules: List[Dict]) -> List[Dict]:
    """Анализирует файл с помощью кастомных правил на основе регулярных выражений."""
    findings = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"⚠️  Could not read file {file_path}: {e}")
        return findings
    
    for line_num, line in enumerate(lines, 1):
        for rule in rules:
            regex_pattern = rule.get('regex', '')
            if regex_pattern and re.search(regex_pattern, line, re.IGNORECASE):
                finding = {
                    'file': file_path,
                    'line': line_num,
                    'severity': rule.get('severity', 'Warning').capitalize(),
                    'rule_id': rule['id'],
                    'message': rule.get('message', ''),
                    'code_snippet': line.strip()
                }
                findings.append(finding)
    
    return findings


def run_swiftlint(config: AnalyzerConfig, target_dir: str) -> List[Dict]:
    """
    Запускает статический анализ кода.
    
    Если SwiftLint доступен - использует его.
    Если нет - использует встроенный анализатор на основе регулярных выражений.
    """
    
    swift_files = find_swift_files(target_dir, config.ignored_paths)
    if not swift_files:
        print("⚠️ No Swift files found in the specified directory.")
        return []

    # Пытаемся использовать SwiftLint
    project_root = os.path.dirname(os.path.abspath(__file__))
    rules_config = os.path.join(project_root, "rules", "custom_rules.yml")
    
    cmd = [
        config.swiftlint_path,
        "lint",
        "--config", rules_config,
        "--reporter", "json",
        "--path", target_dir
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=30)
        raw_json = result.stdout.strip()
        
        if raw_json:
            findings = json.loads(raw_json)
            structured = []
            for item in findings:
                structured.append({
                    "file": item.get("file", ""),
                    "line": item.get("line", 0),
                    "severity": item.get("severity", "Warning").capitalize(),
                    "rule_id": item.get("type", "").replace("custom:", ""),
                    "message": item.get("reason", ""),
                    "code_snippet": ""
                })
            print(f"✓ SwiftLint analysis complete: {len(structured)} issues found")
            return structured
    except FileNotFoundError:
        print("⚠️  SwiftLint not found. Using built-in regex-based analyzer...")
    except json.JSONDecodeError:
        print("⚠️  Failed to parse SwiftLint JSON output. Falling back to built-in analyzer...")
    except subprocess.TimeoutExpired:
        print("⚠️  SwiftLint timed out. Falling back to built-in analyzer...")
    except Exception as e:
        print(f"⚠️  SwiftLint execution failed: {e}. Using built-in analyzer...")
    
    # Встроенний анализатор на основе регулярных выражений
    print("🔍 Running built-in static analyzer...")
    rules = load_custom_rules(rules_config)
    
    if not rules:
        print("⚠️  No custom rules loaded. Analysis will be skipped.")
        return []
    
    all_findings = []
    for swift_file in swift_files:
        file_findings = analyze_file_with_rules(swift_file, rules)
        all_findings.extend(file_findings)
    
    print(f"✓ Built-in analyzer complete: {len(all_findings)} issues found")
    return all_findings