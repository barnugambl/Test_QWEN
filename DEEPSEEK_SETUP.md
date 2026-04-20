# 🚀 Настройка DeepSeek API на macOS

## Шаг 1: Получение API ключа DeepSeek

1. Перейдите на сайт [https://platform.deepseek.com](https://platform.deepseek.com)
2. Зарегистрируйтесь или войдите в аккаунт
3. Перейдите в раздел **API Keys** (обычно в профиле или настройках)
4. Нажмите **Create New API Key**
5. Скопируйте полученный ключ (начинается с `sk-...`)
   - ⚠️ **Важно**: Ключ показывается только один раз! Сохраните его в надежном месте.

## Шаг 2: Установка ключа в конфигурацию

Откройте файл конфигурации и замените тестовый ключ на ваш реальный:

```bash
nano config/analyzer.yaml
```

Найдите строку 19 и замените:
```yaml
api_key: "sk-7f3b8a9c2d1e4f5g6h7i8j9k0l1m2n3o" # Замените на ваш реальный ключ DeepSeek
```

На ваш ключ:
```yaml
api_key: "sk-ваш_реальный_ключ_здесь"
```

Сохраните файл (`Ctrl+O`, `Enter`, `Ctrl+X` в nano).

## Шаг 3: Проверка установки зависимостей

Убедитесь, что установлена библиотека `openai` (уже установлено):

```bash
pip install openai requests pyyaml
```

## Шаг 4: Запуск анализатора

```bash
python main.py --input ./TestApp --config config/analyzer.yaml --generate-reports
```

## 💰 Стоимость DeepSeek API

DeepSeek предлагает очень низкие цены:
- **DeepSeek-Coder**: ~$0.00014 за 1K токенов (вход) / ~$0.00028 (выход)
- **DeepSeek-Chat**: ~$0.00014 за 1K токенов (вход) / ~$0.00028 (выход)

Один анализ небольшого проекта (~1000 строк кода) стоит менее $0.01!

## 🔍 Проверка работы

Если всё настроено правильно, вы увидите:
```
🔍 Verifying finding 1/3: security_plain_text_token
  ✓ Verified: True (confidence: 0.85)
```

Если видите ошибку `401 Unauthorized` - ключ неверный или не активирован.
Если видите `400 Bad Request` - проверьте название модели в конфиге.

## 🛠️ Troubleshooting

### Ошибка "Connection refused"
- Вы пытаетесь использовать Ollama, но он не запущен
- Решение: используйте DeepSeek API (измените `provider: "deepseek"` в конфиге)

### Ошибка "401 Unauthorized"
- Неверный API ключ
- Решение: перепроверьте ключ в config/analyzer.yaml

### Ошибка "400 invalid_request_error"
- Неправильное название модели
- Решение: используйте `deepseek-chat` или `deepseek-coder`

### Медленная работа
- DeepSeek API может отвечать 5-30 секунд в зависимости от размера кода
- Это нормально для облачного API

## 📝 Альтернатива: Локальный Ollama (полностью бесплатно)

Если хотите запускать модель локально без интернета:

```bash
# 1. Установите Ollama
brew install ollama

# 2. Запустите сервер
ollama serve &

# 3. Скачайте модель
ollama pull deepseek-coder:6.7b

# 4. Измените config/analyzer.yaml:
# provider: "ollama"
# ollama:
#   model_name: "deepseek-coder:6.7b"
```

Но для начала рекомендуем DeepSeek API - это быстрее и проще!
