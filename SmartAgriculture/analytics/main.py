import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Analytics service started")
    while True:
        logger.info("Analytics service running...")
        time.sleep(60)

if __name__ == "__main__":
    main()