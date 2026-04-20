# 🚀 Быстрый старт с DeepSeek API

## 1️⃣ Получите API ключ DeepSeek

1. Зайдите на [https://platform.deepseek.com](https://platform.deepseek.com)
2. Зарегистрируйтесь (можно через Google/GitHub)
3. Перейдите в раздел **API Keys** в личном кабинете
4. Нажмите **Create API Key**
5. Скопируйте ключ (начинается с `sk-...`)

## 2️⃣ Вставьте ключ в конфиг

Откройте файл `config/analyzer.yaml` и замените строку:

```yaml
deepseek:
  api_key: "sk-ВАШ_РЕАЛЬНЫЙ_КЛЮЧ_ЗДЕСЬ"  # <-- ВСТАВЬТЕ СЮДА
```

На ваш реальный ключ, например:
```yaml
deepseek:
  api_key: "sk-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
```

## 3️⃣ Запустите анализатор

```bash
cd /workspace
python main.py --input ./TestApp --config config/analyzer.yaml --generate-reports
```

## ✅ Ожидаемый результат

```
🔍 Loading configuration...
🛠 Running static analysis (SwiftLint + custom rules)...
📊 Found 2 potential issues:
  ERROR TestApp/Vulnerable.swift:L3 | security_plain_text_token
  WARNING TestApp/Vulnerable.swift:L4 | security_insecure_logging

🤖 Starting LLM verification...
🔍 Verifying finding 1/2: security_plain_text_token
  ✓ Verified: True (confidence: 0.92)
🔍 Verifying finding 2/2: security_insecure_logging
  ✓ Verified: True (confidence: 0.87)

✓ LLM verification complete. 2/2 issues confirmed.
📄 Generating reports...
✓ Reports generated successfully!
```

## 💰 Стоимость

DeepSeek API очень дешевый:
- ~$0.14 за 1 млн токенов на вход
- ~$0.28 за 1 млн токенов на выход
- Один анализ iOS приложения (~100 файлов) стоит ~$0.01-0.05

## 🔧 Если возникли ошибки

### Ошибка 401 Unauthorized
```
⚠️  deepseek API error: 401 - {"error": "Invalid API key"}
```
→ Проверьте, что вставили правильный API ключ без лишних пробелов

### Ошибка 429 Too Many Requests
```
⚠️  deepseek API error: 429 - {"error": "Rate limit exceeded"}
```
→ Подождите немного или увеличьте timeout в конфиге

### Ошибка кодировки
```
'latin-1' codec can't encode characters
```
→ Обновлена версия кода, теперь использует UTF-8 кодирование

## 📝 Тестовый пример

Файл `TestApp/Vulnerable.swift` содержит 2 уязвимости для тестирования:
1. Сохранение токена в UserDefaults без шифрования
2. Вывод чувствительных данных в логи

Попробуйте запустить анализ на этом примере!
