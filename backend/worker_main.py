import time
import logging
from app.core.config_registry import ConfigRegistry
from app.dependencies import worker_daemon
from app.database.session import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker_main")

if __name__ == "__main__":
    logger.info("Initializing DB for Worker...")
    init_db()
    
    logger.info("Starting Worker Daemon...")
    worker_daemon.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping Worker Daemon...")
        worker_daemon.stop()
