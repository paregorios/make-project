"""
Python 3 script template (changeme)
"""

import argparse
from functools import wraps
import inspect
import logging
import os
import re
import sys
import traceback

DEFAULT_LOG_LEVEL = logging.INFO
POSITIONAL_ARGUMENTS = sorted([
    ['-l', '--loglevel', logging.getLevelName(DEFAULT_LOG_LEVEL),
        'desired logging level (' +
        'case-insensitive string: DEBUG, INFO, WARNING, or ERROR'],
    ['-v', '--verbose', False, 'verbose output (logging level == INFO)'],
    ['-vv', '--veryverbose', False,
        'very verbose output (logging level == DEBUG)'],
    ['-c', '--create', True, 'create directory at indicated path'],
])


def arglogger(func):
    """
    decorator to log argument calls to functions
    """
    @wraps(func)
    def inner(*args, **kwargs):
        logger = logging.getLogger(func.__name__)
        logger.debug("called with arguments: %s, %s" % (args, kwargs))
        return func(*args, **kwargs)
    return inner


@arglogger
def main(args):
    """
    main function
    """
    logger = logging.getLogger(sys._getframe().f_code.co_name)
    where = args['where']
    create_directory = arg


@arglogger
def create_directory(where):
    """
    create the project directory at the indicated path
    """
    pass


@arglogger
def create_venv(where):
    """
    set up python virtual environment at the indicate path
    """
    pass


@arglogger
def create_git(where):
    """
    create git repository
    """
    pass


if __name__ == "__main__":
    log_level = DEFAULT_LOG_LEVEL
    log_level_name = logging.getLevelName(log_level)
    logging.basicConfig(level=log_level)

    # report script name and docstring
    fn_this = inspect.stack()[0][1].strip()
    title_this = __doc__.strip()
    logging.info(': '.join((fn_this, title_this)))
    try:
        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        for p in POSITIONAL_ARGUMENTS:
            d = {
                'default': p[2],
                'help': p[3]
            }
            if type(p[2]) == bool:
                d['action'] = 'store_true'
            parser.add_argument(
                p[0],
                p[1],
                **d)
        parser.add_argument(
            'where',
            type=str,
            help='path to desired project directory')
        args = parser.parse_args()
        if args.loglevel is not None:
            args_log_level = re.sub('\s+', '', args.loglevel.strip().upper())
            try:
                log_level = getattr(logging, args_log_level)
            except AttributeError:
                logging.error(
                    "command line option to set log_level failed "
                    "because '%s' is not a valid level name; using %s"
                    % (args_log_level, log_level_name))
        if args.veryverbose:
            log_level = logging.DEBUG
        elif args.verbose:
            log_level = logging.INFO
        log_level_name = logging.getLevelName(log_level)
        logging.getLogger().setLevel(log_level)
        if log_level != DEFAULTLOGLEVEL:
            logging.warning(
                "logging level changed to %s via command line option"
                % log_level_name)
        else:
            logging.info("using default logging level: %s" % log_level_name)
        logging.debug("command line: '%s'" % ' '.join(sys.argv))
        main(args)
        sys.exit(0)
    except KeyboardInterrupt as e:  # Ctrl-C
        raise e
    except SystemExit as e:  # sys.exit()
        raise e
    except Exception as e:
        print("ERROR, UNEXPECTED EXCEPTION")
        print(str(e))
        traceback.print_exc()
        os._exit(1)
