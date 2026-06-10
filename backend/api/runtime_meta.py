import os

RUNTIME_VERSION = os.environ.get("RUNTIME_VERSION", "1.0.0")
RUNTIME_ENV = os.environ.get("RUNTIME_ENV", "development").lower()


def runtime_environment_label() -> str:
    mapping = {
        "development": "Development",
        "dev": "Development",
        "staging": "Staging",
        "stage": "Staging",
        "production": "Production",
        "prod": "Production",
    }
    return mapping.get(RUNTIME_ENV, RUNTIME_ENV.capitalize())
