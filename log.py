__all__ = ['getLogger', 'INFO', 'WARN', 'DEBUG', 'TRACE', 'ERROR', 'FATAL']

import logging
from logging import getLogger, INFO, WARN, DEBUG, ERROR, FATAL

TRACE = logging.TRACE = DEBUG - 5
logging.addLevelName(TRACE, 'TRACE')

FORMAT = '%(asctime)s %(name)s[%(process)d] [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = getLogger()

# logFileName = "gcp-logging-retrieved.log"
# logFormatter = logging.Formatter(FORMAT)
# fileHandler = logging.handlers.RotatingFileHandler(
#     logFileName, maxBytes=50000000, backupCount=10)
# fileHandler.setFormatter(logFormatter)
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)
# logger.addHandler(fileHandler)


def __add_options(parser):
    levels = ('TRACE', 'DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')
    parser.add_argument('-v', '--log-level',
                        choices=levels, metavar="LEVEL",
                        default='INFO',
                        dest='loglevel',
                        help=('Amount of detail in build-time console messages. '
                              'LEVEL may be one of %s (default: %%(default)s).'
                              % ', '.join(levels))
                        )


def __process_options(parser, opts):
    try:
        level = getattr(logging, opts.loglevel.upper())
    except AttributeError:
        parser.error('Unknown log level `%s`' % opts.loglevel)
    else:
        logger.setLevel(level)
