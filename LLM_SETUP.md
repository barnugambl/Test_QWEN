# Интеграция с бесплатными LLM (DeepSeek/Ollama)

Данное решение поддерживает два варианта использования бесплатных языковых моделей для верификации уязвимостей:

## Вариант 1: Ollama (Локальный запуск, полностью бесплатно)

### Преимущества:
- ✅ Полностью бесплатно
- ✅ Не требует интернета (работает локально)
- ✅ Конфиденциальность (код не отправляется на внешние серверы)
- ✅ Поддержка множества моделей (DeepSeek, CodeLlama, Mistral и др.)

### Установка:

1. **Установите Ollama:**
   ```bash
   # Для Linux
   curl -fsSL https://ollama.com/install.sh | sh
   
   # Для macOS
   brew install ollama
   
   # Для Windows - скачайте с https://ollama.com
   ```

2. **Запустите Ollama сервис:**
   ```bash
   ollama serve
   ```

3. **Загрузите модель DeepSeek Coder:**
   ```bash
   ollama pull deepseek-coder:6.7b
   ```
   
   Или другие модели для кода:
   ```bash
   ollama pull codellama:7b
   ollama pull llama3
   ollama pull mistral
   ```

4. **Настройте конфигурацию** (`config/analyzer.yaml`):
   ```yaml
   llm_integration:
     enabled: true
     provider: "ollama"
     
     ollama:
       model_name: "deepseek-coder:6.7b"
       base_url: "http://localhost:11434"
       timeout: 120
     
     confidence_threshold: 0.6
   ```

5. **Запустите анализатор:**
   ```bash
   python main.py --input ./TestApp --config config/analyzer.yaml --generate-reports
   ```

---

## Вариант 2: DeepSeek API (Облачный, очень дешево)

### Преимущества:
- ✅ Очень низкая стоимость (~$0.00014/1K токенов)
- ✅ Высокое качество анализа
- ✅ Не требует мощного железа
- ✅ Быстрые ответы

### Регистрация и получение ключа:

1. **Зарегистрируйтесь на платформе DeepSeek:**
   - Посетите https://platform.deepseek.com/
   - Создайте аккаунт
   - Перейдите в раздел API Keys

2. **Получите API ключ:**
   - Нажмите "Create API Key"
   - Скопируйте ключ (он покажется только один раз!)

3. **Настройте конфигурацию** (`config/analyzer.yaml`):
   ```yaml
   llm_integration:
     enabled: true
     provider: "deepseek"
     
     deepseek:
       api_key: "sk-xxxxxxxxxxxxxxxxxxxxxxxx"  # Ваш ключ
       model_name: "deepseek-coder"
       base_url: "https://api.deepseek.com"
     
     confidence_threshold: 0.6
   ```

4. **Запустите анализатор:**
   ```bash
   python main.py --input ./TestApp --config config/analyzer.yaml --generate-reports
   ```

---

## Сравнение вариантов

| Критерий | Ollama (локально) | DeepSeek API |
|----------|-------------------|--------------|
| Стоимость | Бесплатно | ~$0.01-0.10 за анализ проекта |
| Требует интернет | Нет | Да |
| Конфиденциальность | Полная | Код отправляется на сервер |
| Требования к железу | 8-16 GB RAM | Любые |
| Скорость | Зависит от GPU/CPU | Быстро |
| Качество моделей | Хорошее | Отличное |

---

## Примеры использования

### Только статический анализ (без LLM):
```bash
python main.py --input ./TestApp --config config/analyzer.yaml
```

### С LLM верификацией через Ollama:
```bash
python main.py --input ./TestApp --config config/analyzer.yaml --generate-reports
```

### Принудительное включение LLM:
```bash
python main.py --input ./TestApp --config config/analyzer.yaml --llm-enabled --generate-reports
```

---

## Рекомендуемые модели для Ollama

Для анализа кода iOS/Swift рекомендуются следующие модели:

1. **deepseek-coder:6.7b** - лучшее соотношение качество/скорость
2. **codellama:7b-instruct** - специализирована для кода
3. **llama3:8b-instruct** - универсальная, хорошее понимание контекста
4. **mistral:7b-instruct** - быстрая и эффективная

Для загрузки:
```bash
ollama pull deepseek-coder:6.7b
ollama pull codellama:7b-instruct
ollama pull llama3:8b-instruct
ollama pull mistral:7b-instruct
```

---

## Troubleshooting

### Ollama не отвечает:
```bash
# Проверьте статус сервиса
systemctl status ollama

# Перезапустите
ollama serve
```

### Модель слишком медленная:
- Используйте модели меньшего размера (3b вместо 7b)
- Увеличьте таймаут в конфигурации
- Запустите на GPU (если доступен)

### DeepSeek API ошибка авторизации:
- Проверьте правильность API ключа
- Убедитесь, что на счету есть средства
- Проверьте лимиты API

---

## Дополнительные ресурсы

- [Ollama официальная документация](https://ollama.com/)
- [DeepSeek API документация](https://platform.deepseek.com/docs)
- [Модели для кода на HuggingFace](https://huggingface.co/models?pipeline_tag=text-generation&tags=code)
