# Гибридный анализатор безопасности iOS-приложений

Решение для автоматического выявления небезопасных практик обработки пользовательских данных в iOS-приложениях, разработанное в рамках учебной практики.

## 📋 Описание

Проект реализует гибридный подход к анализу безопасности кода Swift, сочетающий:
- **Статический анализ** на основе правил (pattern matching)
- **LLM-верификацию** для подтверждения уязвимостей с помощью больших языковых моделей
- **Генерацию отчетов** в форматах JSON и HTML

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                    main.py                                   │
│              (Точка входа, CLI интерфейс)                    │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   scanner.py     │ │  llm_verifier.py │ │report_generator.py│
│  Статический     │ │   LLM-модуль     │ │  Генерация       │
│  анализатор      │ │   верификации    │ │  отчетов         │
└──────────────────┘ └──────────────────┘ └──────────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ custom_rules.yml │ │   OpenAI API     │ │  JSON/HTML/CSV   │
│  Правила анализа │ │   (опционально)  │ │   отчеты         │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

## 🚀 Быстрый старт

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Базовое использование

```bash
# Запуск анализа с генерацией отчетов
python main.py --input /path/to/ios/project --generate-reports --project-name "My App"

# Запуск с включенной LLM-верификацией (требуется API ключ)
python main.py --input /path/to/ios/project --generate-reports --llm-enabled --project-name "My App"
```

### Параметры командной строки

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `--input` | Путь к директории с iOS проектом | **Обязательный** |
| `--config` | Путь к конфигурационному файлу | `config/analyzer.yaml` |
| `--output` | Директория для отчетов | `reports` |
| `--project-name` | Название проекта для отчетов | `iOS Project` |
| `--llm-enabled` | Включить LLM-верификацию | `False` |
| `--generate-reports` | Генерировать отчеты | `False` |

## 📁 Структура проекта

```
/workspace
├── main.py                 # Точка входа, CLI интерфейс
├── scanner.py              # Модуль статического анализа
├── llm_verifier.py         # Модуль LLM-верификации
├── report_generator.py     # Модуль генерации отчетов
├── config.py               # Конфигурационные модели
├── config/
│   └── analyzer.yaml       # Конфигурация анализатора
├── rules/
│   └── custom_rules.yml    # Правила безопасности
├── TestApp/                # Тестовое приложение
│   └── Vulnerable.swift
└── reports/                # Сгенерированные отчеты
```

## 🔍 Правила безопасности

Анализатор проверяет код на соответствие требованиям OWASP MASVS:

| Правило | Описание | Стандарт OWASP |
|---------|----------|----------------|
| `security_plain_text_token` | Хранение токенов/API ключей в UserDefaults | MSTG-STORAGE-2 |
| `security_insecure_logging` | Вывод чувствительных данных в логи | MSTG-STORAGE-3, PRIVACY-1 |
| `security_unencrypted_file_storage` | Сохранение данных без шифрования | MSTG-STORAGE-6 |

## 📊 Форматы отчетов

### JSON отчет
Машиночитаемый формат с полной структурой уязвимостей:
```json
{
  "project_info": {
    "name": "My App",
    "analysis_date": "2025-12-30T...",
    "analysis_time_seconds": 1.23
  },
  "summary": {
    "total_issues": 5,
    "confirmed_issues": 3,
    "high_priority_issues": 2
  },
  "issues": [...]
}
```

### HTML отчет
Человекочитаемый отчет с визуализацией:
- Сводная статистика
- Детали каждой уязвимости
- Результаты LLM-верификации
- Подсветкаseverity

## ⚙️ Конфигурация

### config/analyzer.yaml

```yaml
ruleset:
  - security_plain_text_token
  - security_insecure_logging
  - security_unencrypted_file_storage

llm_integration:
  enabled: false
  api_key: ""
  model_name: "gpt-4-turbo"
  confidence_threshold: 0.85

sources_sinks:
  sources: ["UITextField.text", "CLLocationManager.location"]
  sinks: ["UserDefaults.standard.set", "FileManager.write", "print"]

ignored_paths:
  - "Pods/"
  - "Carthage/"
  - "build/"
```

## 🤖 LLM-верификация

Для включения верификации уязвимостей через большие языковые модели:

1. Получите API ключ OpenAI
2. Установите его в конфиге или через переменную окружения:
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```
3. Запустите анализатор с флагом `--llm-enabled`

LLM анализирует каждый найденный паттерн и подтверждает или опровергает уязвимость, снижая количество ложных срабатываний.

## 🧪 Тестирование

```bash
# Запуск на тестовом приложении
python main.py --input TestApp --generate-reports --project-name "TestApp Demo"
```

## 📈 Метрики качества

Для оценки эффективности анализатора используется сравнение с эталонными данными:

- **Precision (Точность)**: доля реальных уязвимостей среди всех найденных
- **Recall (Полнота)**: доля найденных уязвимостей среди всех существующих

## 📝 Требования

- Python 3.8+
- Зависимости: `pyyaml`, `pydantic`, `rich`, `requests`
- Опционально: SwiftLint (для расширенного анализа)
- Опционально: OpenAI API key (для LLM-верификации)

## 📄 Лицензия

Проект разработан в рамках учебной практики в КФУ.

## 👥 Авторы

- Терехин Иван Николаевич, группа 11-306
- Руководитель практики: Шахова И.С., старший преподаватель кафедры программной инженерии КФУ

## 📚 Использованные источники

1. OWASP Mobile Application Security Verification Standard (MASVS)
2. MITRE CWE - Common Weakness Enumeration
3. Apple Security Documentation
4. Mobile Security Framework (MobSF)
5. CodeQL - Semantic Code Analysis
