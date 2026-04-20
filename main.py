import argparse
import yaml
from pathlib import Path
from config import AnalyzerConfig
from scanner import run_swiftlint
from rich.console import Console

console = Console()

def load_config(config_path: str) -> AnalyzerConfig:
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return AnalyzerConfig(**data)

def main():
    parser = argparse.ArgumentParser(description="Hybrid iOS Security Analyzer")
    parser.add_argument("--input", required=True, help="Path to iOS project directory")
    parser.add_argument("--config", default="config/analyzer.yaml", help="Path to analyzer config")
    args = parser.parse_args()

    if not Path(args.input).is_dir():
        console.print(f"[red]Error:[/red] Directory '{args.input}' not found.")
        return

    console.print("[bold blue]🔍 Loading configuration...[/bold blue]")
    cfg = load_config(args.config)

    console.print("[bold green]🛠 Running static analysis (SwiftLint + custom rules)...[/bold green]")
    findings = run_swiftlint(cfg, args.input)

    console.print(f"\n[bold]📊 Found {len(findings)} potential issues:[/bold]")
    for f in findings:
        sev_color = "red" if f["severity"] == "Error" else "yellow"
        console.print(f"  [{sev_color}]{f['severity'].upper()}[/] {f['file']}:L{f['line']} | {f['rule_id']}\n    {f['message']}")

    console.print("\n[bold blue]✅ Static analysis complete. Ready for LLM verification & report generation.[/bold blue]")

if __name__ == "__main__":
    main()