from pathlib import Path
import re
from typing import Dict

SEARCH_PATHS = [
    Path(__file__).resolve().parent / "shaders"
]

INCLUDES: Dict[str, str] = {}


def preprocess_shader_source(
    source: str,
) -> str:
    def _sub_include(match):
        name = match.groups()[0]
        if name in INCLUDES:
            return INCLUDES[name]

        for path in SEARCH_PATHS:
            full_name = path / name
            if full_name.exists():
                source = preprocess_shader_source(full_name.read_text())
                INCLUDES[name] = source
                return source
        raise FileNotFoundError(f"Shader file '{name}' not found")

    source = re.sub(r"^\s*#\s*include\s+\"([^\"]+)\s*\"$", _sub_include, source, flags=re.MULTILINE)

    return source
