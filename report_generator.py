import json
import csv
from datetime import datetime
from typing import List, Dict
from pathlib import Path


class ReportGenerator:
    """Модуль генерации отчетов о результатах анализа безопасности."""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_json_report(self, findings: List[Dict], project_name: str, analysis_time: float) -> str:
        """
        Генерирует машиночитаемый JSON-отчет.
        
        Args:
            findings: Список найденных уязвимостей
            project_name: Название проекта
            analysis_time: Время выполнения анализа в секундах
        
        Returns:
            Путь к сгенерированному файлу
        """
        
        # Подсчет статистики
        total_issues = len(findings)
        confirmed_issues = sum(1 for f in findings if f.get('confirmed', False))
        high_priority = sum(1 for f in findings if f.get('severity') == 'Error' and f.get('confirmed', False))
        medium_priority = sum(1 for f in findings if f.get('severity') == 'Warning' and f.get('confirmed', False))
        low_priority = sum(1 for f in findings if f.get('severity') == 'Note' and f.get('confirmed', False))
        
        # Формирование структуры отчета
        report = {
            "project_info": {
                "name": project_name,
                "analysis_date": datetime.now().isoformat(),
                "analysis_time_seconds": round(analysis_time, 2)
            },
            "summary": {
                "total_issues": total_issues,
                "confirmed_issues": confirmed_issues,
                "high_priority_issues": high_priority,
                "medium_priority_issues": medium_priority,
                "low_priority_issues": low_priority
            },
            "issues": []
        }
        
        # Добавление деталей по каждой уязвимости
        for finding in findings:
            issue = {
                "rule_id": finding.get('rule_id', 'unknown'),
                "severity": finding.get('severity', 'Warning'),
                "file_path": finding.get('file', ''),
                "line_number": finding.get('line', 0),
                "message": finding.get('message', ''),
                "snippet": finding.get('code_snippet', ''),
                "verified_by": finding.get('verification_source', 'swiftlint'),
                "confirmed": finding.get('confirmed', False),
                "llm_verification": {
                    "verified": finding.get('llm_verified', False),
                    "confidence": finding.get('llm_confidence', 0.0),
                    "reason": finding.get('llm_reason', '')
                } if finding.get('verification_source') == 'llm' else None
            }
            report["issues"].append(issue)
        
        # Сохранение отчета
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"vulnerability_report_{timestamp}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def generate_html_report(self, findings: List[Dict], project_name: str, analysis_time: float) -> str:
        """
        Генерирует человекочитаемый HTML-отчет.
        
        Args:
            findings: Список найденных уязвимостей
            project_name: Название проекта
            analysis_time: Время выполнения анализа в секундах
        
        Returns:
            Путь к сгенерированному файлу
        """
        
        # Подсчет статистики
        total_issues = len(findings)
        confirmed_issues = sum(1 for f in findings if f.get('confirmed', False))
        high_priority = sum(1 for f in findings if f.get('severity') == 'Error' and f.get('confirmed', False))
        medium_priority = sum(1 for f in findings if f.get('severity') == 'Warning' and f.get('confirmed', False))
        
        # Формирование HTML
        html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Отчет по безопасности - {project_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f7;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .summary-card.high {{
            border-left: 4px solid #dc3545;
        }}
        .summary-card.medium {{
            border-left: 4px solid #ffc107;
        }}
        .summary-card.low {{
            border-left: 4px solid #28a745;
        }}
        .summary-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        .summary-card .label {{
            color: #666;
            font-size: 0.9em;
        }}
        .issue {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .issue-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid #eee;
        }}
        .severity-badge {{
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            color: white;
        }}
        .severity-error {{
            background-color: #dc3545;
        }}
        .severity-warning {{
            background-color: #ffc107;
            color: #333;
        }}
        .severity-note {{
            background-color: #17a2b8;
        }}
        .issue-meta {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}
        .code-snippet {{
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 15px;
            font-family: 'SF Mono', Monaco, Consolas, monospace;
            font-size: 0.9em;
            overflow-x: auto;
            margin: 15px 0;
        }}
        .llm-verification {{
            background-color: #e8f4fd;
            border-left: 4px solid #17a2b8;
            padding: 15px;
            margin-top: 15px;
            border-radius: 0 5px 5px 0;
        }}
        .llm-verified {{
            background-color: #d4edda;
            border-left-color: #28a745;
        }}
        .llm-not-verified {{
            background-color: #fff3cd;
            border-left-color: #ffc107;
        }}
        .no-issues {{
            text-align: center;
            padding: 50px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .no-issues h2 {{
            color: #28a745;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔒 Отчет по безопасности iOS-приложения</h1>
        <p><strong>Проект:</strong> {project_name}</p>
        <p><strong>Дата анализа:</strong> {datetime.now().strftime("%d.%m.%Y %H:%M")}</p>
        <p><strong>Время выполнения:</strong> {analysis_time:.2f} сек.</p>
    </div>
    
    <div class="summary">
        <div class="summary-card">
            <div class="number">{total_issues}</div>
            <div class="label">Всего найдено</div>
        </div>
        <div class="summary-card high">
            <div class="number">{high_priority}</div>
            <div class="label">Высокий приоритет</div>
        </div>
        <div class="summary-card medium">
            <div class="number">{medium_priority}</div>
            <div class="label">Средний приоритет</div>
        </div>
        <div class="summary-card low">
            <div class="number">{confirmed_issues}</div>
            <div class="label">Подтверждено</div>
        </div>
    </div>
"""
        
        if not findings:
            html_content += """
    <div class="no-issues">
        <h2>✅ Уязвимостей не обнаружено</h2>
        <p>Анализ кода не выявил потенциальных проблем безопасности.</p>
    </div>
"""
        else:
            html_content += "    <h2>📋 Найденные уязвимости</h2>\n"
            
            for i, finding in enumerate(findings, 1):
                severity_class = {
                    'Error': 'severity-error',
                    'Warning': 'severity-warning',
                    'Note': 'severity-note'
                }.get(finding.get('severity', 'Warning'), 'severity-warning')
                
                severity_label = {
                    'Error': 'HIGH',
                    'Warning': 'MEDIUM',
                    'Note': 'LOW'
                }.get(finding.get('severity', 'Warning'), 'MEDIUM')
                
                verified_badge = "✅" if finding.get('confirmed', False) else "⚠️"
                
                llm_section = ""
                if finding.get('verification_source') == 'llm':
                    llm_class = "llm-verified" if finding.get('llm_verified', False) else "llm-not-verified"
                    llm_status = "Подтверждено LLM" if finding.get('llm_verified', False) else "Не подтверждено LLM"
                    llm_section = f"""
                <div class="llm-verification {llm_class}">
                    <strong>🤖 Верификация LLM:</strong> {llm_status}<br>
                    <strong>Уверенность:</strong> {finding.get('llm_confidence', 0.0):.0%}<br>
                    <strong>Обоснование:</strong> {finding.get('llm_reason', 'Нет данных')}
                </div>
"""
                
                code_snippet = finding.get('snippet', finding.get('code_snippet', ''))
                snippet_html = f'<div class="code-snippet"><code>{self._escape_html(code_snippet)}</code></div>' if code_snippet else ''
                
                html_content += f"""
    <div class="issue">
        <div class="issue-header">
            <span><strong>#{i}</strong> {finding.get('rule_id', 'unknown')}</span>
            <span class="severity-badge {severity_class}">{severity_label}</span>
        </div>
        <div class="issue-meta">
            📁 <strong>Файл:</strong> {finding.get('file', 'N/A')}<br>
            📍 <strong>Строка:</strong> {finding.get('line', 'N/A')}<br>
            {verified_badge} <strong>Статус:</strong> {'Подтверждено' if finding.get('confirmed', False) else 'Требует проверки'}
        </div>
        <p><strong>Описание:</strong> {finding.get('message', 'Нет описания')}</p>
        {snippet_html}
        {llm_section}
    </div>
"""
        
        html_content += """
</body>
</html>
"""
        
        # Сохранение отчета
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"vulnerability_report_{timestamp}.html"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(filepath)
    
    def generate_comparison_csv(self, hybrid_findings: List[Dict], mobsf_findings: List[Dict], 
                                ground_truth: List[Dict]) -> str:
        """
        Генерирует CSV-файл для сравнения эффективности инструментов.
        
        Args:
            hybrid_findings: Результаты гибридного инструмента
            mobsf_findings: Результаты MobSF
            ground_truth: Эталонная разметка
        
        Returns:
            Путь к сгенерированному файлу
        """
        
        # Сбор всех типов уязвимостей
        all_vuln_types = set()
        for f in hybrid_findings + mobsf_findings + ground_truth:
            all_vuln_types.add(f.get('rule_id', 'unknown'))
        
        # Формирование строк сравнения
        rows = []
        for vuln_type in all_vuln_types:
            hybrid_detected = any(f.get('rule_id') == vuln_type and f.get('confirmed', False) for f in hybrid_findings)
            mobsf_detected = any(f.get('rule_id') == vuln_type for f in mobsf_findings)
            gt_exists = any(f.get('rule_id') == vuln_type for f in ground_truth)
            
            # Определение результата
            if gt_exists and hybrid_detected:
                result = "True Positive"
            elif gt_exists and not hybrid_detected:
                result = "False Negative"
            elif not gt_exists and hybrid_detected:
                result = "False Positive"
            else:
                result = "True Negative"
            
            rows.append({
                'vulnerability_type': vuln_type,
                'hybrid_tool_detected': 'Да' if hybrid_detected else 'Нет',
                'mobsf_detected': 'Да' if mobsf_detected else 'Нет',
                'ground_truth': 'Да' if gt_exists else 'Нет',
                'result': result
            })
        
        # Сохранение CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comparison_report_{timestamp}.csv"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['vulnerability_type', 'hybrid_tool_detected', 'mobsf_detected', 'ground_truth', 'result']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        return str(filepath)
    
    def _escape_html(self, text: str) -> str:
        """Экранирует специальные HTML-символы."""
        if not text:
            return ""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))
    
    def generate_all_reports(self, findings: List[Dict], project_name: str, 
                            analysis_time: float, mobsf_findings: List[Dict] = None,
                            ground_truth: List[Dict] = None) -> Dict[str, str]:
        """
        Генерирует все типы отчетов.
        
        Returns:
            Словарь с путями к сгенерированным файлам
        """
        reports = {}
        
        reports['json'] = self.generate_json_report(findings, project_name, analysis_time)
        reports['html'] = self.generate_html_report(findings, project_name, analysis_time)
        
        if mobsf_findings is not None and ground_truth is not None:
            reports['comparison'] = self.generate_comparison_csv(
                findings, mobsf_findings, ground_truth
            )
        
        return reports
