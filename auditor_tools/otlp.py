"""Metadata-only adapter for one sanitized OTLP JSON trace export."""

import re

from auditor_tools.contracts import identifier, integer, mapping, sequence


OPERATIONS = {
    "chat", "text_completion", "generate_content", "embeddings",
    "execute_tool", "invoke_agent", "create_agent",
}


def _span_id(value: object, size: int, label: str) -> str:
    if (
        not isinstance(value, str)
        or not re.fullmatch(rf"[0-9a-fA-F]{{{size}}}", value)
        or not int(value, 16)
    ):
        raise ValueError(f"{label} must be a nonzero {size}-character hexadecimal identifier")
    return value.lower()


def _timestamp(value: object) -> int | None:
    if value is None:
        return None
    result = integer(value, "timestamp", strings=True)
    return result if result else None


def normalize_otlp(payload: object, *, source_id: str) -> dict[str, object]:
    source_id = identifier(source_id, "source_id")
    document = mapping(payload, "OTLP export")
    resources = sequence(document.get("resourceSpans"), "resourceSpans")
    spans: list[dict[str, object]] = []
    originals: dict[tuple[str, str], dict[str, object]] = {}
    duplicates = 0
    for resource_index, item in enumerate(resources):
        resource = mapping(item, "resourceSpans item")
        scopes = sequence(resource.get("scopeSpans", []), "scopeSpans")
        for scope_index, item in enumerate(scopes):
            scope = mapping(item, "scopeSpans item")
            for span_index, item in enumerate(sequence(scope.get("spans", []), "spans")):
                span = mapping(item, "span")
                trace_id = _span_id(span.get("traceId"), 32, "traceId")
                span_id = _span_id(span.get("spanId"), 16, "spanId")
                key = (trace_id, span_id)
                if key in originals:
                    if span != originals[key]:
                        raise ValueError("conflicting duplicate span identity")
                    duplicates += 1
                    continue
                originals[key] = span
                parent = span.get("parentSpanId")
                parent_id = (
                    None if parent in (None, "", "0" * 16)
                    else _span_id(parent, 16, "parentSpanId")
                )
                start = _timestamp(span.get("startTimeUnixNano"))
                finish = _timestamp(span.get("endTimeUnixNano"))
                if start is not None and finish is not None and finish < start:
                    raise ValueError("span ends before it starts")
                status = mapping(span.get("status", {}), "span status")
                code = status.get("code", 0)
                if type(code) is not int or code not in (0, 1, 2):
                    raise ValueError("status code must be the OTLP integer enum 0, 1 or 2")
                selected: dict[str, object] = {}
                seen: set[str] = set()
                for item in sequence(span.get("attributes", []), "span attributes"):
                    attribute = mapping(item, "attribute")
                    name = attribute.get("key")
                    if not isinstance(name, str) or name in seen:
                        raise ValueError("span attributes must have unique string keys")
                    seen.add(name)
                    if name in {
                        "gen_ai.operation.name", "gen_ai.usage.input_tokens",
                        "gen_ai.usage.output_tokens",
                    }:
                        selected[name] = mapping(attribute.get("value"), "attribute value")
                operation = "unknown"
                if "gen_ai.operation.name" in selected:
                    value = mapping(selected["gen_ai.operation.name"], "operation")
                    if set(value) != {"stringValue"} or not isinstance(value["stringValue"], str):
                        raise ValueError("operation must have exactly one stringValue")
                    if value["stringValue"] in OPERATIONS:
                        operation = value["stringValue"]
                tokens: dict[str, object] = {}
                for direction in ("input", "output"):
                    field = f"gen_ai.usage.{direction}_tokens"
                    tokens[f"{direction}_tokens"] = None
                    if field in selected:
                        value = mapping(selected[field], "token usage")
                        if set(value) != {"intValue"}:
                            raise ValueError("token usage must have exactly one intValue")
                        tokens[f"{direction}_tokens"] = integer(value["intValue"], "tokens", strings=True)
                spans.append({
                    "trace_id": trace_id, "span_id": span_id, "parent_span_id": parent_id,
                    "source_record": (
                        f"resourceSpans/{resource_index}/scopeSpans/{scope_index}/spans/{span_index}"
                    ),
                    "start_unix_nano": str(start) if start is not None else None,
                    "end_unix_nano": str(finish) if finish is not None else None,
                    "duration_ms": (
                        (finish - start) / 1_000_000
                        if start is not None and finish is not None else None
                    ),
                    "status": {0: "unset", 1: "ok", 2: "error"}[code],
                    "operation": operation, **tokens,
                })
    return {
        "schema": "auditor-traces/1", "adapter": "otlp-json/1",
        "source_id": source_id, "coverage": "unknown",
        "sanitization": "user-confirmed-input; metadata-allowlist-output",
        "duplicates_removed": duplicates, "spans": spans,
        "limitations": [
            "Span status is not task success; spans are not logical calls or request counts.",
            "No retry grouping, token aggregation, pricing, quality or complete coverage inferred.",
            "Names, arbitrary attributes, resource data, events and links are omitted.",
        ],
    }
