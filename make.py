"""
Make a project directory with associated setup
"""

import argparse
import errno
from functools import wraps
import inspect
import logging
import os
import re
import requests
import shutil
import subprocess
import sys
import traceback

DEFAULT_LOG_LEVEL = logging.INFO
POSITIONAL_ARGUMENTS = sorted([
    ['-l', '--loglevel', logging.getLevelName(DEFAULT_LOG_LEVEL),
        'desired logging level (' +
        'case-insensitive string: DEBUG, INFO, WARNING, or ERROR'],
    ['-v', '--verbose', False, 'verbose output (logging level == INFO)'],
    ['-w', '--veryverbose', False,
        'very verbose output (logging level == DEBUG)'],
    ['-c', '--create', False, 'create directory at indicated path'],
    ['-p', '--pyvenv', False, 'create a python virtual environment'],
    ['-n', '--pyver', '3', 'version of python to use in virtual environment'],
    ['-g', '--git', False, 'create a new git repository'],
    ['-s', '--script', False, 'set up with a python script'],
    ['-k', '--package', False, 'set up as a python package'],
    ['-r', '--readme', False, 'add a readme file template'],
    ['-q', '--quiet', False, 'suppress output (logging level == CRITICAL)']
])
GITIGNORE_URLS = [
    'https://raw.githubusercontent.com/github/gitignore/master/Global/' +
    'OSX.gitignore',
    'https://raw.githubusercontent.com/github/gitignore/master/' +
    'Python.gitignore'
    ]
TEMPLATES = {
    'script-2': '~/Documents/files/P/python-script-template/template2.py',
    'script-3': '~/Documents/files/P/python-script-template/template3.py'
}
PACKAGE_URLS = [
    'https://raw.githubusercontent.com/pypa/sampleproject/master/setup.py',
    'https://raw.githubusercontent.com/pypa/sampleproject/master/setup.cfg',
    'https://raw.githubusercontent.com/pypa/sampleproject/master/MANIFEST.in'
]


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
    # logger = logging.getLogger(sys._getframe().f_code.co_name)

    where = os.path.abspath(args.where)
    if args.script and args.package:
        raise ValueError('cannot create both a script and a package')
    if args.create:
        create_directory(where)
    if args.pyvenv:
        create_venv(where, args.pyver)
    if args.git:
        create_git(where)
    if args.readme:
        create_readme(where, args.git)
    if args.script:
        init_script(where, args.pyver, args.git)
    if args.package:
        init_package(where, args.git)


@arglogger
def create_directory(where):
    """
    create the project directory at the indicated path
    """
    logger = logging.getLogger(sys._getframe().f_code.co_name)
    try:
        os.makedirs(where)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(where):
            logger.critical(
                'script run with directory creation, but {0} already exists'
                ''.format(where))
            sys.exit(1)
    logger.info('created new project directory at {0}'.format(where))


@arglogger
def create_readme(where, git=False):
    """
    create an initial readme file
    """
    pass


@arglogger
def create_venv(where, python_version):
    """
    set up python virtual environment
    """
    logger = logging.getLogger(sys._getframe().f_code.co_name)
    v = '/usr/local/bin/python{0}'.format(python_version)
    env_dir = '~/Envs/{0}'.format(os.path.basename(where))
    if os.path.exists(env_dir):
        logger.critical(
            'script run with venv creation, but {0} already exists'
            ''.format(env_dir))
        sys.exit(1)
    # somewhy following returns failure code 1 even when successful,
    # so can't try
    cmd = 'mkvirtualenv -v -p {0} {1} && deactivate'.format(v, env_dir)
    run(cmd, check=False)  # mkvirtualenv returns non-zero code despite success


@arglogger
def create_git(where):
    """
    create git repository
    """
    logger = logging.getLogger(sys._getframe().f_code.co_name)
    cmd = 'git init {0}'.format(where)
    run(cmd)
    logger.info('initialized git repository at {0}'.format(where))
    logger.debug('trying to set up .gitignore')
    for url in GITIGNORE_URLS:
        logger.debug('requesting {0}'.format(url))
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(where + '/.gitignore', 'ab') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        else:
            raise Exception('aiiiiieeeee')
            sys.exit(1)
    git_it(where, '.gitignore', 'intial values for .gitignore from: {0}'
           ''.format(', '.join(GITIGNORE_URLS)))
    logger.info('instantiated .gitignore and committed it')


@arglogger
def init_script(where, py_ver, git=False):
    """
    include a python script template
    """
    logger = logging.getLogger(sys._getframe().f_code.co_name)
    src = TEMPLATES['script-{0}'.format(py_ver)]
    logger.debug('src: {0}'.format(src))
    src = os.path.expanduser(src)
    logger.debug('src: {0}'.format(src))
    src = os.path.abspath(src)
    logger.debug('src: {0}'.format(src))
    dest_fn = '{0}.py'.format(os.path.basename(where))
    dest = '{0}/{1}'.format(where, dest_fn)
    shutil.copy2(src, dest)
    logger.debug('copied {0} to {1}'.format(src, dest))
    if git:
        git_it(os.path.dirname(dest), dest_fn,
               'include default script template')
    logger.info('added script template as {0}'.format(dest_fn))


@arglogger
def init_package(where, git=False):
    """
    set up as a python package
    """
    logger = logging.getLogger(sys._getframe().f_code.co_name)
    for url in PACKAGE_URLS:
        fn = url.rsplit('/', 1)[-1]
        fpath = os.path.join(where, fn)
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(fpath, 'ab') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        else:
            raise Exception('aiiiiieeeee')
            sys.exit(1)
        git_it(where, fn, 'intial content for {0} from: {1}'
               ''.format(fn, url))
        logger.info('instantiated {0} and committed it'.format(fpath))


@arglogger
def git_it(where, what, msg):
    """
    add and commit something to the git repository
    """
    cmd = 'git add {0} && git commit -m "{1}"'.format(what, msg)
    run(cmd, where)


@arglogger
def run(cmd, where=None, check=True):
    """
    use subprocess to execute a desired command in the shell
    """
    logger = logging.getLogger(sys._getframe().f_code.co_name)
    run_params = [
        'bash',
        '-c',
        '. ~/.bash_profile'
    ]
    if where is not None:
        run_params[-1] += ' && cd {0}'.format(where)
    run_params[-1] += ' && {0}'.format(cmd)
    logger.debug('run_params: \n      {0}'.format('\n      '.join(run_params)))
    try:
        result = subprocess.run(
            run_params,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=check).stdout
    except subprocess.CalledProcessError as e:
        logger.critical('subprocess execution failed with status code '
                        '{0}:\n    '.format(e.returncode) +
                        'command was: "{0}\n      "'.format(run_params) +
                        'captured output:      ' +
                        '\n      '.join(result.decode('utf-8').split('\n')))


if __name__ == "__main__":
    log_level = DEFAULT_LOG_LEVEL
    log_level_name = logging.getLevelName(log_level)
    logging.basicConfig(level=log_level)

    try:
        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        for p in POSITIONAL_ARGUMENTS:
            d = {
                'help': p[3]
            }
            if type(p[2]) == bool:
                if p[2] is False:
                    d['action'] = 'store_true'
                    d['default'] = False
                else:
                    d['action'] = 'store_false'
                    d['default'] = True
            else:
                d['default'] = p[2]
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
        elif args.quiet:
            log_level = logging.CRITICAL
        log_level_name = logging.getLevelName(log_level)
        logging.getLogger().setLevel(log_level)
        fn_this = inspect.stack()[0][1].strip()
        title_this = __doc__.strip()
        logging.info(': '.join((fn_this, title_this)))
        if log_level != DEFAULT_LOG_LEVEL:
            logging.warning(
                "logging level changed to %s via command line option"
                % log_level_name)
        else:
            logging.info("using default logging level: %s" % log_level_name)
        logging.debug("command line: '%s'" % ' '.join(sys.argv))
        try:
            main(args)
        except ValueError as e:
            logging.critical(e)
            sys.exit(1)
        except NotImplementedError as e:
            logging.critical(e)
            sys.exit(1)
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
