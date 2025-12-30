"""
Service Container
Lightweight Dependency Injection container.
Removes singleton dependencies and enables easier testing.
"""
import logging
from typing import Type, TypeVar, Dict, Any

T = TypeVar('T')

class ServiceContainer:
    _instance = None
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._logger = logging.getLogger("ServiceContainer")

    def register(self, service_type: Type[T], instance: Any) -> None:
        """Register a concrete instance for a specific service type/protocol."""
        # Optional: Strict type checking could go here
        self._services[service_type] = instance
        # self._logger.info(f"Registered service: {service_type.__name__}")

    def resolve(self, service_type: Type[T]) -> T:
        """Retrieve a registered service."""
        try:
            return self._services[service_type]
        except KeyError:
            raise RuntimeError(f"Service {service_type.__name__} not registered.")
