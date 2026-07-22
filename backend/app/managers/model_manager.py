import importlib
import pkgutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from app.core.exceptions import EngineNotFoundException
from app.core.logging import logger
from app.engines.base_engine import BaseAudioEngine
from app.engines.plugins.f5tts import F5TTSAudioEngine
from app.engines.plugins.mock import MockAudioEngine


class ModelManager:
    """Model Manager handling dynamic plugin discovery, engine registration, and loading lifecycle."""

    def __init__(self):
        self._engines: Dict[str, BaseAudioEngine] = {}
        self._active_engine_name: Optional[str] = None
        self._discover_and_register_plugins()

    def _discover_and_register_plugins(self) -> None:
        """Register built-in engines and dynamically discover plugin engine classes."""
        # 1. Register built-in engines explicitly
        self.register_engine(MockAudioEngine())
        self.register_engine(F5TTSAudioEngine())

        # 2. Dynamic discovery under app.engines.plugins
        try:
            import app.engines.plugins as plugins_pkg
            for _, modname, _ in pkgutil.walk_packages(plugins_pkg.__path__, plugins_pkg.__name__ + "."):
                mod = importlib.import_module(modname)
                for obj_name in dir(mod):
                    obj = getattr(mod, obj_name)
                    if (
                        isinstance(obj, type)
                        and issubclass(obj, BaseAudioEngine)
                        and obj is not BaseAudioEngine
                    ):
                        instance = obj()
                        self.register_engine(instance)
        except Exception as e:
            logger.debug(f"Plugin auto-discovery scan complete: {e}")

    def register_engine(self, engine: BaseAudioEngine) -> None:
        """Register an engine instance."""
        name = engine.engine_name.lower()
        self._engines[name] = engine
        logger.info(f"Registered audio engine plugin: '{name}' ({engine.description})")

    def get_engine(self, name: str) -> BaseAudioEngine:
        """Fetch engine plugin by name."""
        key = name.lower()
        if key not in self._engines:
            raise EngineNotFoundException(name)
        return self._engines[key]

    def list_available_engines(self) -> List[Dict[str, Any]]:
        """List metadata for all registered engines."""
        return [
            {
                "name": engine.engine_name,
                "description": engine.description,
                "available": engine.is_available(),
            }
            for engine in self._engines.values()
        ]

    def load_model_to_device(self, engine_name: str, device_idx: int) -> bool:
        """Loads a model onto a specific device if not already loaded."""
        from app.managers.gpu_manager import gpu_manager
        from app.core.execution_context import ExecutionContext
        
        if gpu_manager.is_model_loaded(device_idx, engine_name):
            return True
            
        engine = self.get_engine(engine_name)
        context = ExecutionContext(device_index=device_idx, engine_name=engine_name, job_id="sys_load")
        
        success = engine.load_model(Path("."), context=context)
        if success:
            gpu_manager.mark_model_loaded(device_idx, engine_name)
        return success

    def unload_model_from_device(self, engine_name: str, device_idx: int) -> bool:
        """Unloads a model from a specific device."""
        from app.managers.gpu_manager import gpu_manager
        from app.core.execution_context import ExecutionContext
        
        if not gpu_manager.is_model_loaded(device_idx, engine_name):
            return True
            
        engine = self.get_engine(engine_name)
        context = ExecutionContext(device_index=device_idx, engine_name=engine_name, job_id="sys_unload")
        
        success = engine.unload_model(context=context)
        if success:
            gpu_manager.mark_model_unloaded(device_idx, engine_name)
        return success
