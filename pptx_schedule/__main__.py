"""Entry point for ``python -m pptx_schedule``."""

from .cli import main

if __name__ == "__main__":  # pragma: no cover - module execution
    raise SystemExit(main())
