import logging
import sys

from backend import run

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

LOG: logging.Logger = logging.getLogger(__name__)


def main() -> None:
    LOG.info("Starting the matchmaking system...")
    run()
    LOG.info("Matchmaking system has finished.")


if __name__ == "__main__":
    main()
