import logging
import sys

from app.core.settings import settings

logger = logging.getLogger(__name__)

def setup_logging() -> None:
    """Configure application-wide logging."""

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format=("%(asctime)s | %(levelname)s | %(name)s | %(message)s"),
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )
