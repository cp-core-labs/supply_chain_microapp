from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    root_dir: Path = Path(__file__).resolve().parents[2]
    data_dir: Path = root_dir / "data"

    @property
    def historical_sales_path(self) -> Path:
        return self.data_dir / "historical_sales.csv"

    @property
    def suppliers_path(self) -> Path:
        return self.data_dir / "suppliers_lead_time.csv"


APP_CONFIG = AppConfig()
