"""
AI CyberShield — Application Configuration Loader

Central configuration management using pydantic-settings.
Loads configuration from environment variables and .env files.
"""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide configuration loaded from environment variables.

    All values can be overridden via environment variables or a .env file.
    The .env file is loaded automatically from the project root.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ──────────────────────────────────────────────
    # App Settings
    # ──────────────────────────────────────────────
    app_name: str = "AI CyberShield"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True
    api_version: str = "0.1.0"
    secret_key: str = "change-me"

    # ──────────────────────────────────────────────
    # Database Settings
    # ──────────────────────────────────────────────
    database_url: str = "sqlite:///./data.db"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_echo: bool = False

    # ──────────────────────────────────────────────
    # Model Settings
    # ──────────────────────────────────────────────
    model_path: str = "./ml/artifacts/model.pkl"
    model_type: str = "xgboost"
    model_version: str = "0.1.0"
    model_threshold: float = 0.5
    model_device: str = "cpu"
    model_verbosity: int = 0

    # ──────────────────────────────────────────────
    # ML Pipeline Settings
    # ──────────────────────────────────────────────
    random_state: int = 42
    n_jobs: int = -1
    train_test_split: float = 0.2
    train_val_split: float = 0.1
    cv_folds: int = 5
    scoring_metric: str = "f1_macro"
    early_stopping_rounds: int = 50

    # ──────────────────────────────────────────────
    # Logging Settings
    # ──────────────────────────────────────────────
    log_level: str = "INFO"
    log_format: str = "json"
    log_output: str = "./logs"
    log_file_path: str = "./logs/cybershield.log"
    log_max_bytes: int = 10_485_760
    log_backup_count: int = 5

    # ──────────────────────────────────────────────
    # Dataset Settings
    # ──────────────────────────────────────────────
    dataset_source: str = "CICIDS2017"
    dataset_target_column: str = "Label"
    dataset_sample_size: float = 1.0
    dataset_random_seed: int = 42
    dataset_raw_path: str = "./datasets/raw"
    dataset_processed_path: str = "./datasets/processed"

    # ──────────────────────────────────────────────
    # Paths
    # ──────────────────────────────────────────────
    @property
    def project_root(self) -> Path:
        """Return the project root directory."""
        return Path(__file__).resolve().parent.parent.parent

    @property
    def log_dir(self) -> Path:
        """Return the logging directory."""
        return self.project_root / "logs"


# Singleton instance for application-wide use
settings = Settings()
