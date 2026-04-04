import os, logging, time
from logging.handlers import TimedRotatingFileHandler

# Setup audit logger with daily rotation
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("audit_logger")
logger.setLevel(logging.INFO)

# Create handler that rotates at midnight (or daily)
handler = TimedRotatingFileHandler(
    filename=f"{LOG_DIR}/auditlog-{time.strftime('%Y-%m-%d')}.log", # base filename
    when="midnight",                                                # rotate at midnight
    interval=1,                                                     # every 1 day
    backupCount=30,                                                 # keep last 30 days
    encoding="utf-8"
)

# Set a specific format
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)
logger.addHandler(handler)

# # Prevent propagation to root logger to avoid duplicate logs
# audit_logger.propagate = False
