from typing import List, Literal
from pydantic import BaseModel, Field

Severity = Literal["critical", "high", "medium", "low", "info"]
Category = Literal[
    "injection",
    "auth",
    "secrets",
    "crypto",
    "rce",
    "ssrf",
    "path_traversal",
    "deserialization",
    "deps",
    "config",
    "logging",
    "dos",
    "supply_chain",
    "other",
]

class Finding(BaseModel):
    id: str = Field(..., description="Stable id for eval matching, e.g., 'SQLI-1'")
    severity: Severity
    category: Category
    file: str
    line: str = Field(..., description="e.g. L10-L25 or unknown")
    title: str
    evidence: str = Field(..., description="Quote relevant code or describe the exact pattern.")
    impact: str
    recommendation: str

class ScanResult(BaseModel):
    summary: str
    overall_risk_score: int = Field(..., ge=0, le=100)
    findings: List[Finding]