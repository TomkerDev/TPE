import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Preprocessing service started")
    while True:
        logger.info("Preprocessing service running...")
        time.sleep(60)

if __name__ == "__main__":
    main()