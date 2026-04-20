import argparse
import yaml
import time
from pathlib import Path
from config import AnalyzerConfig, LLMConfig
from scanner import run_swiftlint
from llm_verifier import LLMVerifier
from report_generator import ReportGenerator
from rich.console import Console

console = Console()

def load_config(config_path: str) -> AnalyzerConfig:
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    # Обработка новой структуры конфигурации LLM
    llm_data = data.get('llm_integration', {})
    
    # Создаем LLMConfig с правильными полями
    llm_config = LLMConfig(
        enabled=llm_data.get('enabled', False),
        provider=llm_data.get('provider', 'ollama'),
        confidence_threshold=llm_data.get('confidence_threshold', 0.6)
    )
    
    # Обрабатываем настройки для Ollama
    if 'ollama' in llm_data:
        ollama_cfg = llm_data['ollama']
        llm_config.ollama_model_name = ollama_cfg.get('model_name')
        llm_config.ollama_base_url = ollama_cfg.get('base_url')
        llm_config.ollama_timeout = ollama_cfg.get('timeout')
    
    # Обрабатываем настройки для DeepSeek
    if 'deepseek' in llm_data:
        deepseek_cfg = llm_data['deepseek']
        llm_config.api_key = deepseek_cfg.get('api_key')
        llm_config.deepseek_model_name = deepseek_cfg.get('model_name')
        llm_config.deepseek_base_url = deepseek_cfg.get('base_url')
    
    # Обратная совместимость со старым форматом
    if 'api_key' in llm_data and llm_data['api_key']:
        llm_config.api_key = llm_data['api_key']
    if 'model_name' in llm_data and llm_data['model_name']:
        llm_config.model_name = llm_data['model_name']
    
    # Обновляем данные конфигурации
    data['llm_integration'] = llm_config
    
    return AnalyzerConfig(**data)

def main():
    parser = argparse.ArgumentParser(description="Hybrid iOS Security Analyzer")
    parser.add_argument("--input", required=True, help="Path to iOS project directory")
    parser.add_argument("--config", default="config/analyzer.yaml", help="Path to analyzer config")
    parser.add_argument("--output", default="reports", help="Output directory for reports")
    parser.add_argument("--project-name", default="iOS Project", help="Project name for reports")
    parser.add_argument("--llm-enabled", action="store_true", help="Enable LLM verification")
    parser.add_argument("--generate-reports", action="store_true", help="Generate JSON and HTML reports")
    args = parser.parse_args()

    if not Path(args.input).is_dir():
        console.print(f"[red]Error:[/red] Directory '{args.input}' not found.")
        return

    start_time = time.time()
    
    console.print("[bold blue]🔍 Loading configuration...[/bold blue]")
    cfg = load_config(args.config)
    
    # Переопределяем настройку LLM если указан флаг --llm-enabled
    if args.llm_enabled:
        cfg.llm_integration.enabled = True

    console.print("[bold green]🛠 Running static analysis (SwiftLint + custom rules)...[/bold green]")
    findings = run_swiftlint(cfg, args.input)

    console.print(f"\n[bold]📊 Found {len(findings)} potential issues:[/bold]")
    for f in findings:
        sev_color = "red" if f["severity"] == "Error" else "yellow"
        console.print(f"  [{sev_color}]{f['severity'].upper()}[/] {f['file']}:L{f['line']} | {f['rule_id']}\n    {f['message']}")

    # LLM верификация
    if cfg.llm_integration.enabled:
        console.print("\n[bold blue]🤖 Starting LLM verification...[/bold blue]")
        verifier = LLMVerifier(cfg.llm_integration)
        findings = verifier.verify_batch(findings, args.input)
        
        confirmed_count = sum(1 for f in findings if f.get('confirmed', False))
        console.print(f"\n[bold green]✓ LLM verification complete. {confirmed_count}/{len(findings)} issues confirmed.[/bold green]")
    else:
        console.print("\n[yellow]⚠️  LLM verification is disabled. Use --llm-enabled flag to enable.[/yellow]")
        # Помечаем все находки как неподтвержденные
        for f in findings:
            f['confirmed'] = False
            f['verification_source'] = 'swiftlint'

    analysis_time = time.time() - start_time
    
    # Генерация отчетов
    if args.generate_reports:
        console.print("\n[bold blue]📄 Generating reports...[/bold blue]")
        generator = ReportGenerator(args.output)
        reports = generator.generate_all_reports(
            findings=findings,
            project_name=args.project_name,
            analysis_time=analysis_time
        )
        
        console.print("\n[bold green]✓ Reports generated successfully![/bold green]")
        for report_type, filepath in reports.items():
            console.print(f"  • {report_type.upper()}: [cyan]{filepath}[/cyan]")

    console.print(f"\n[bold blue]✅ Analysis complete in {analysis_time:.2f} seconds.[/bold blue]")

if __name__ == "__main__":
    main()