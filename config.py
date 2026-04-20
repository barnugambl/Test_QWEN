from pydantic import BaseModel, Field
from typing import List, Optional

class LLMConfig(BaseModel):
    enabled: bool = False
    api_key: Optional[str] = None
    model_name: str = "gpt-4-turbo"
    confidence_threshold: float = 0.8

class SourcesSinksConfig(BaseModel):
    sources: List[str] = Field(default_factory=list)
    sinks: List[str] = Field(default_factory=list)

class AnalyzerConfig(BaseModel):
    ruleset: List[str] = Field(default_factory=list)
    llm_integration: LLMConfig = Field(default_factory=LLMConfig)
    sources_sinks: SourcesSinksConfig = Field(default_factory=SourcesSinksConfig)
    ignored_paths: List[str] = Field(default_factory=lambda: ["Pods/", "Carthage/", "build/", ".git/"])
    swiftlint_path: str = "swiftlint"