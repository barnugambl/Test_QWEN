from pydantic import BaseModel, Field
from typing import List, Optional

class OllamaConfig(BaseModel):
    model_name: str = "deepseek-coder:6.7b"
    base_url: str = "http://localhost:11434"
    timeout: int = 120

class DeepSeekConfig(BaseModel):
    api_key: Optional[str] = None
    model_name: str = "deepseek-coder"
    base_url: str = "https://api.deepseek.com"

class LLMConfig(BaseModel):
    enabled: bool = False
    provider: str = "ollama"  # 'ollama' или 'deepseek'
    
    # Настройки для Ollama (локально)
    ollama_model_name: Optional[str] = None  # будет использовано если provider='ollama'
    ollama_base_url: Optional[str] = None
    ollama_timeout: Optional[int] = None
    
    # Настройки для DeepSeek (API)
    api_key: Optional[str] = None  # будет использовано если provider='deepseek'
    deepseek_model_name: Optional[str] = None
    deepseek_base_url: Optional[str] = None
    
    # Общие настройки
    model_name: Optional[str] = None  # устаревшее поле для обратной совместимости
    confidence_threshold: float = 0.6

class SourcesSinksConfig(BaseModel):
    sources: List[str] = Field(default_factory=list)
    sinks: List[str] = Field(default_factory=list)

class AnalyzerConfig(BaseModel):
    ruleset: List[str] = Field(default_factory=list)
    llm_integration: LLMConfig = Field(default_factory=LLMConfig)
    sources_sinks: SourcesSinksConfig = Field(default_factory=SourcesSinksConfig)
    ignored_paths: List[str] = Field(default_factory=lambda: ["Pods/", "Carthage/", "build/", ".git/"])
    swiftlint_path: str = "swiftlint"