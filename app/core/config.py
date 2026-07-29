import os
from dataclasses import dataclass
from pathlib import Path


def _load_env_file() -> None:
	"""Load .env values into process environment if they are not already set."""
	env_file = Path(__file__).resolve().parents[2] / ".env"
	if not env_file.exists():
		return

	for raw_line in env_file.read_text(encoding="utf-8").splitlines():
		line = raw_line.strip()
		if not line or line.startswith("#") or "=" not in line:
			continue
		key, value = line.split("=", 1)
		os.environ.setdefault(key.strip(), value.strip())


@dataclass(frozen=True)
class Settings:
	DATABASE_NAME: str
	DATABASE_USER: str
	DATABASE_PASSWORD: str
	DATABASE_HOST: str
	DATABASE_PORT: int


def _required_env(key: str) -> str:
	value = os.getenv(key)
	if not value:
		raise ValueError(f"Missing required environment variable: {key}")
	return value


def _build_settings() -> Settings:
	_load_env_file()
	return Settings(
		DATABASE_NAME=_required_env("DATABASE_NAME"),
		DATABASE_USER=_required_env("DATABASE_USER"),
		DATABASE_PASSWORD=_required_env("DATABASE_PASSWORD"),
		DATABASE_HOST=_required_env("DATABASE_HOST"),
		DATABASE_PORT=int(os.getenv("DATABASE_PORT", "5432")),
	)


settings = _build_settings()
