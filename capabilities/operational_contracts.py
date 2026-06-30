"""Operational contract engine.

Declarative input/output contracts for work entering or leaving a capability.
A contract lists required fields and simple type expectations; the engine
validates payloads against it. Generic schema enforcement — no business rules.
"""

from typing import Any

_TYPE_MAP = {
    "str": str,
    "int": int,
    "float": (int, float),
    "bool": bool,
    "dict": dict,
    "list": list,
}


class OperationalContracts:
    _contracts: dict[str, dict[str, Any]] = {}

    @classmethod
    def define(cls, name: str, required: dict[str, str]) -> dict[str, Any]:
        """required maps field_name -> type name (str/int/float/bool/dict/list)."""
        cls._contracts[name] = {"name": name, "required": required}
        return cls._contracts[name]

    @classmethod
    def validate(cls, name: str, payload: dict[str, Any]) -> dict[str, Any]:
        contract = cls._contracts.get(name)
        if not contract:
            return {"valid": False, "violations": [f"unknown contract: {name}"]}
        violations: list[str] = []
        for field, type_name in contract["required"].items():
            if field not in payload:
                violations.append(f"missing field: {field}")
                continue
            expected = _TYPE_MAP.get(type_name)
            if expected and not isinstance(payload[field], expected):
                violations.append(f"field {field} must be {type_name}")
        return {"valid": not violations, "violations": violations, "contract": name}

    @classmethod
    def list_contracts(cls) -> list[dict[str, Any]]:
        return list(cls._contracts.values())

    @classmethod
    def reset(cls) -> None:
        cls._contracts = {}
