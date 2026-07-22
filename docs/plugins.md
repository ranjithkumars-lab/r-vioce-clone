# Plugin Development Guide

Voice Studio supports dynamically loaded audio synthesis engines. You can add new Text-to-Speech (TTS) models without altering the core pipeline.

## Creating a Plugin

1. Navigate to `backend/app/engines/plugins/`.
2. Create a new Python file (e.g., `my_engine.py`).
3. Inherit from `BaseAudioEngine` located in `app.engines.base_engine`.

### Example

```python
from pathlib import Path
from typing import Any, Dict, Optional
from app.engines.base_engine import BaseAudioEngine
from app.core.execution_context import ExecutionContext

class MyCustomEngine(BaseAudioEngine):
    @property
    def engine_name(self) -> str:
        return "my_engine"

    @property
    def description(self) -> str:
        return "Custom experimental TTS engine"

    def is_available(self) -> bool:
        # Check for dependencies/CUDA
        return True

    def load_model(self, model_dir: Path, context: Optional[ExecutionContext] = None) -> bool:
        # Load weights to context.device_str
        return True

    def unload_model(self, context: Optional[ExecutionContext] = None) -> bool:
        # Release memory from context.device_str
        return True

    def synthesize(
        self,
        text: str,
        reference_audio_path: Path,
        output_path: Path,
        speed: float = 1.0,
        options: Optional[Dict[str, Any]] = None,
        context: Optional[ExecutionContext] = None,
    ) -> Path:
        # Generate audio and save to output_path
        return output_path
```

## Registration

You do NOT need to register your plugin manually. The `ModelManager` automatically discovers all subclasses of `BaseAudioEngine` imported within the `plugins` package. Simply ensure your module is imported in `backend/app/engines/plugins/__init__.py`.
