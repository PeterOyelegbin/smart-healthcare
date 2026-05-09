import os, logging, time, sys
from logging.handlers import TimedRotatingFileHandler
from pythonjsonlogger import jsonlogger

# Determine if running in serverless or containerized environment
is_serverless = os.getenv('VERCEL') or os.getenv('SERVERLESS') or os.getenv('AWS_LAMBDA_FUNCTION_NAME')
is_docker = os.path.exists('/.dockerenv') or os.getenv('DOCKER_CONTAINER')

# Setup audit logger
logger = logging.getLogger("audit_logger")
logger.setLevel(logging.INFO)

if is_serverless or is_docker:
    # Use StreamHandler for serverless environments (logs to stdout/stderr)
    handler = logging.StreamHandler(sys.stdout)
    # Use JSON formatter for structured logging
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
else:
    # Setup file logging with daily rotation for local/development
    LOG_DIR = "logs"
    os.makedirs(LOG_DIR, exist_ok=True)

    handler = TimedRotatingFileHandler(
        filename=f"{LOG_DIR}/auditlog-{time.strftime('%Y-%m-%d')}.log",
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    # Use standard formatter for file logs
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

handler.setFormatter(formatter)
logger.addHandler(handler)

# Prevent propagation to root logger to avoid duplicate logs
logger.propagate = False
