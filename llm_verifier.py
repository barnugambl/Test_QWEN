import json
import requests
from typing import Dict, Optional, List
from config import LLMConfig, DeepSeekConfig, OllamaConfig


class LLMVerifier:
    """Модуль верификации уязвимостей с использованием больших языковых моделей (DeepSeek/Ollama)."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.enabled = config.enabled if config else False
        self.provider = (config.provider or "ollama").lower()
        self.confidence_threshold = config.confidence_threshold if config else 0.6
        
        # Инициализация настроек провайдеров
        self.ollama_config: Optional[OllamaConfig] = config.ollama if config else None
        self.deepseek_config: Optional[DeepSeekConfig] = config.deepseek if config else None
        
        # Настройки для разных провайдеров с fallback на старые поля
        if self.provider == 'ollama':
            if self.ollama_config:
                self.model_name = self.ollama_config.model_name
                self.base_url = self.ollama_config.base_url
                self.timeout = self.ollama_config.timeout
            else:
                # Fallback на старые поля или дефолтные значения
                self.model_name = config.ollama_model_name if hasattr(config, 'ollama_model_name') and config.ollama_model_name else "deepseek-coder:6.7b"
                self.base_url = config.ollama_base_url if hasattr(config, 'ollama_base_url') and config.ollama_base_url else "http://localhost:11434"
                self.timeout = config.ollama_timeout if hasattr(config, 'ollama_timeout') and config.ollama_timeout else 120
            self.api_key = None
            
        elif self.provider == 'deepseek':
            if self.deepseek_config:
                self.model_name = self.deepseek_config.model_name
                self.base_url = self.deepseek_config.base_url
                self.api_key = self.deepseek_config.api_key
            else:
                # Fallback на старые поля или дефолтные значения
                self.model_name = config.deepseek_model_name if hasattr(config, 'deepseek_model_name') and config.deepseek_model_name else "deepseek-chat"
                self.base_url = config.deepseek_base_url if hasattr(config, 'deepseek_base_url') and config.deepseek_base_url else "https://api.deepseek.com"
                self.api_key = config.api_key if hasattr(config, 'api_key') else None
            self.timeout = 60
            
            # Проверка наличия API ключа
            if self.enabled and not self.api_key:
                print(f"⚠️  DeepSeek enabled but API key is missing. LLM verification will be skipped.")
                self.enabled = False
        else:
            print(f"⚠️  Unknown provider: {self.provider}, defaulting to ollama")
            self.provider = 'ollama'
            self.model_name = "deepseek-coder:6.7b"
            self.base_url = "http://localhost:11434"
            self.api_key = None
            self.timeout = 120
    
    def create_prompt(self, code_snippet: str, context: str, rule_id: str) -> str:
        """Создает структурированный промпт для LLM."""
        
        rule_descriptions = {
            "security_plain_text_token": "сохраняется ли в этом коде конфиденциальная пользовательская data (например, пароль, токен, API ключ) в ненадежное хранилище UserDefaults без шифрования?",
            "security_insecure_logging": "выводится ли в этом коде чувствительная информация (пароли, токены, персональные данные, геолокация) в системные логи (print, NSLog, os_log)?",
            "security_unencrypted_file_storage": "сохраняются ли в этом коде конфиденциальные данные в файловую систему без предварительного шифрования?"
        }
        
        question = rule_descriptions.get(rule_id, "содержит ли этот код потенциальную уязвимость безопасности, связанную с обработкой пользовательских данных?")
        
        prompt = f"""Проанализируй следующий фрагмент кода Swift на наличие утечки конфиденциальных данных.

Код:
```swift
{code_snippet}
```

Контекст:
{context}

Вопрос: {question}

Ответь строго в формате JSON:
{{"is_vulnerable": boolean, "confidence": number (от 0.0 до 1.0), "reason": string}}

Важно: ответ должен быть только JSON объектом, без дополнительного текста."""
        
        return prompt
    
    def parse_llm_response(self, response_text: str) -> Optional[Dict]:
        """Парсит ответ от LLM и возвращает структурированные данные."""
        try:
            # Попытка найти JSON в ответе
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                return None
            
            json_str = response_text[start_idx:end_idx]
            data = json.loads(json_str)
            
            # Валидация структуры ответа
            if not isinstance(data, dict):
                return None
            
            required_keys = ['is_vulnerable', 'confidence', 'reason']
            if not all(key in data for key in required_keys):
                return None
            
            # Проверка типов
            if not isinstance(data['is_vulnerable'], bool):
                return None
            if not isinstance(data['confidence'], (int, float)):
                return None
            if not isinstance(data['reason'], str):
                return None
            
            # Нормализация confidence
            data['confidence'] = max(0.0, min(1.0, float(data['confidence'])))
            
            return data
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"⚠️  Failed to parse LLM response: {e}")
            return None
    
    def verify_finding(self, code_snippet: str, context: str, rule_id: str) -> Dict:
        """
        Верифицирует найденную уязвимость с помощью LLM (DeepSeek или Ollama).
        
        Returns:
            Dict с результатами верификации:
            - verified: bool (подтверждена ли уязвимость)
            - confidence: float (уровень уверенности)
            - reason: str (обоснование)
            - source: str ("llm" или "skipped")
        """
        
        if not self.enabled:
            return {
                "verified": False,
                "confidence": 0.0,
                "reason": "LLM verification is disabled",
                "source": "skipped"
            }
        
        prompt = self.create_prompt(code_snippet, context, rule_id)
        
        if self.provider == 'ollama':
            # Локальный запуск через Ollama API
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 500
                }
            }
            
            url = f"{self.base_url}/api/generate"
            headers = {"Content-Type": "application/json"}
            
        elif self.provider == 'deepseek':
            # DeepSeek API (совместим с OpenAI форматом)
            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "Ты эксперт по безопасности iOS-приложений. Твоя задача - анализировать код Swift на наличие уязвимостей, связанных с обработкой пользовательских данных."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 500
            }
            
            url = f"{self.base_url}/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
        else:
            return {
                "verified": False,
                "confidence": 0.0,
                "reason": f"Unknown provider: {self.provider}",
                "source": "error"
            }
        
        # Кодируем payload в UTF-8 явно для избежания проблем с кодировкой
        import json as json_module
        json_payload = json_module.dumps(payload, ensure_ascii=False).encode('utf-8')
        
        try:
            response = requests.post(
                url,
                headers=headers,
                data=json_payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                print(f"⚠️  {self.provider} API error: {response.status_code} - {response.text}")
                return {
                    "verified": False,
                    "confidence": 0.0,
                    "reason": f"API error: {response.status_code}",
                    "source": "error"
                }
            
            response_data = response.json()
            
            # Извлечение ответа в зависимости от провайдера
            if self.provider == 'ollama':
                llm_output = response_data.get('response', '')
            elif self.provider == 'deepseek':
                llm_output = response_data['choices'][0]['message']['content']
            else:
                llm_output = ''
            
            parsed = self.parse_llm_response(llm_output)
            
            if parsed is None:
                return {
                    "verified": False,
                    "confidence": 0.0,
                    "reason": "Failed to parse LLM response",
                    "source": "parse_error"
                }
            
            is_confirmed = parsed['is_vulnerable'] and parsed['confidence'] >= self.confidence_threshold
            
            return {
                "verified": is_confirmed,
                "confidence": parsed['confidence'],
                "reason": parsed['reason'],
                "source": "llm"
            }
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️  LLM request failed: {e}")
            return {
                "verified": False,
                "confidence": 0.0,
                "reason": f"Request error: {str(e)}",
                "source": "error"
            }
        except Exception as e:
            print(f"⚠️  Unexpected error during LLM verification: {e}")
            return {
                "verified": False,
                "confidence": 0.0,
                "reason": f"Unexpected error: {str(e)}",
                "source": "error"
            }
    
    def verify_batch(self, findings: List[Dict], target_dir: str) -> List[Dict]:
        """
        Верифицирует набор найденных уязвимостей.
        
        Args:
            findings: Список уязвимостей от статического анализатора
            target_dir: Путь к директории с исходным кодом
        
        Returns:
            Обновленный список уязвимостей с результатами LLM-верификации
        """
        from pathlib import Path
        
        verified_findings = []
        
        for i, finding in enumerate(findings):
            print(f"\n🔍 Verifying finding {i+1}/{len(findings)}: {finding['rule_id']}")
            
            # Извлекаем контекст из файла
            file_path = finding.get('file', '')
            line_number = finding.get('line', 1)
            
            code_snippet = ""
            context = ""
            
            if file_path and Path(file_path).exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # Извлекаем строку с уязвимостью
                    if 0 < line_number <= len(lines):
                        code_snippet = lines[line_number - 1].strip()
                    
                    # Извлекаем контекст (функцию или класс)
                    start_line = max(0, line_number - 10)
                    end_line = min(len(lines), line_number + 5)
                    context = ''.join(lines[start_line:end_line])
                    
                except Exception as e:
                    print(f"⚠️  Could not read file {file_path}: {e}")
            
            # Верификация через LLM
            llm_result = self.verify_finding(code_snippet, context, finding['rule_id'])
            
            # Добавляем результаты верификации к находке
            enhanced_finding = finding.copy()
            enhanced_finding['llm_verified'] = llm_result['verified']
            enhanced_finding['llm_confidence'] = llm_result['confidence']
            enhanced_finding['llm_reason'] = llm_result['reason']
            enhanced_finding['verification_source'] = llm_result['source']
            
            # Если LLM подтвердила уязвимость, помечаем как окончательную
            if llm_result['verified']:
                enhanced_finding['confirmed'] = True
            else:
                # Если LLM отключена или не подтвердила, оставляем как потенциальную
                enhanced_finding['confirmed'] = not self.enabled
            
            verified_findings.append(enhanced_finding)
            print(f"  ✓ Verified: {llm_result['verified']} (confidence: {llm_result['confidence']:.2f})")
        
        return verified_findings
