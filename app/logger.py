import logging
import sys

# get logger
logger = logging.getLogger()

# create formatter
formater = logging.Formatter(fmt="[%(levelname)s] %(asctime)s %(message)s")


# create handlers
stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler("logfile.log")

# set formatter
stream_handler.setFormatter(formater)
file_handler.setFormatter(formater)

# add handlers to the logger
logger.handlers = [
    stream_handler,
    file_handler
]


# set log-level
logger.setLevel(logging.WARNING)
