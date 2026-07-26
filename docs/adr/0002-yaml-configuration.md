# ADR-0002: YAML-Based Configuration Management

## Status
Accepted

## Date
2026-07-26

## Context
The platform requires a flexible configuration system that can manage dataset paths, model parameters, API settings, and logging levels across different environments (development, testing, production). Hardcoding these values or using only environment variables becomes unwieldy as the number of parameters grows.

## Decision
Adopt YAML as the primary configuration format, with `.env` files for secrets only.

- Configuration files are stored in a `config/` directory with environment-specific overrides (`config.default.yaml`, `config.prod.yaml`).
- Sensitive values (database passwords, API keys) are referenced via `${ENV_VAR}` placeholders and resolved at runtime from the environment.
- Pydantic `BaseSettings` is used to load and validate the combined configuration at application startup.

## Alternatives Considered
- **Pure `.env` files**: Rejected — flat key-value format lacks structure for nested configuration (e.g., model parameters under a `model:` key).
- **TOML**: Viable alternative but YAML is more widely adopted in the ML ecosystem (e.g., Hydra, MLflow).
- **JSON**: Rejected — less readable and no comment support.

## Consequences
- Configuration is human-readable, hierarchical, and self-documenting.
- Secrets remain in `.env` (`.gitignore`d) while non-sensitive defaults are version-controlled.
- Runtime validation catches misconfigurations early.
