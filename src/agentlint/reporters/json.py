from __future__ import annotations

import json
from typing import Any

from agentlint.models import Issue, Resource


def render_json(issues: list[Issue], resources: list[Resource] | None = None) -> str:
    payload: dict[str, Any] = {
        "issues": [issue.to_dict() for issue in issues],
    }
    if resources is not None:
        payload["resources"] = [
            {
                "id": resource.id,
                "tool": resource.tool.value,
                "kind": resource.kind.value,
                "name": resource.name,
                "path": str(resource.path),
                "content_type": resource.content_type.value,
                "refs": [
                    {
                        "to": {
                            "tool": (
                                ref.to_selector.tool.value
                                if ref.to_selector.tool
                                else None
                            ),
                            "kind": (
                                ref.to_selector.kind.value
                                if ref.to_selector.kind
                                else None
                            ),
                            "name": ref.to_selector.name,
                            "path": ref.to_selector.path,
                        },
                        "ref_type": ref.ref_type.value,
                        "raw": ref.raw,
                    }
                    for ref in resource.refs
                ],
            }
            for resource in resources
        ]
    return json.dumps(payload, indent=2, sort_keys=True)
