"""
Make a project directory with associated setup
"""

import argparse
import errno
import frontmatter
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
    ['-q', '--quiet', False, 'suppress output (logging level == CRITICAL)'],
    ['-x', '--license', 'agpl-3.0', 'license to use ("none" is an option)']
])
GITIGNORE_URLS = [
    'https://raw.githubusercontent.com/github/gitignore/master/Global/' +
    'OSX.gitignore',
    'https://raw.githubusercontent.com/github/gitignore/master/' +
    'Python.gitignore'
    ]
template_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                            'templates')
TEMPLATES = {
    'script-2': os.path.join(template_dir, 'script-template-2.py'),
    'script-3': os.path.join(template_dir, 'script-template-3.py'),
    'readme': os.path.join(template_dir, 'README.md'),
    'requirements': os.path.join(template_dir, 'requirements_dev.txt')
}
PACKAGE_URLS = [
    'https://raw.githubusercontent.com/pypa/sampleproject/master/setup.py',
    'https://raw.githubusercontent.com/pypa/sampleproject/master/setup.cfg',
    'https://raw.githubusercontent.com/pypa/sampleproject/master/MANIFEST.in'
]
PACKAGE_SUBDIRECTORIES = [
    ('scripts', True, []),
    ('tests', True, [])
]
LICENSE_FIXES = {
    'cal': {
        'prefix': ('https://raw.githubusercontent.com/github/'
                   'choosealicense.com/gh-pages/_licenses/'),
        'suffix': '.txt'
    }
}
LICENSES = {
    'afl-3.0': ('Academic Free License v3.0', 'cal'),
    'agpl-3.0': ('GNU Affero General Public License v3.0', 'cal'),
    'apache-2.0': ('Apache License 2.0', 'cal'),
    'artistic-2.0': ('Artistic License 2.0', 'cal'),
    'bsd-2-clause': ('BSD 2-clause "Simplified" License', 'cal'),
    'bsd-3-clause-clear': ('BSD 3-clause Clear License', 'cal'),
    'bsd-3-clause': ('BSD 3-clause "New" or "Revised" License', 'cal'),
    'cc-by-4.0': ('Creative Commons Attribution 4.0', 'cal'),
    'cc-by-sa-4.0': ('Creative Commons Attribution Share Alike 4.0', 'cal'),
    'cc0-1.0': ('Creative Commons Zero v1.0 Universal', 'cal'),
    'epl-1.0': ('Eclipse Public License 1.0', 'cal'),
    'eupl-1.1': ('European Union Public License 1.1', 'cal'),
    'gpl-2.0': ('GNU General Public License v2.0', 'cal'),
    'gpl-3.0': ('GNU General Public License v3.0', 'cal'),
    'isc': ('ISC License', 'cal'),
    'lgpl-2.1': ('GNU Lesser General Public License v2.1', 'cal'),
    'lgpl-3.0': ('GNU Lesser General Public License v3.0', 'cal'),
    'lppl-1.3c': ('LaTeX Project Public License v1.3c', 'cal'),
    'mit': ('MIT License', 'cal'),
    'mpl-2.0': ('Mozilla Public License 2.0', 'cal'),
    'ms-pl': ('Microsoft Public License', 'cal'),
    'ms-rl': ('Microsoft Reciprocal License', 'cal'),
    'ofl-1.1': ('SIL Open Font License 1.1', 'cal'),
    'osl-3.0': ('Open Software License 3.0', 'cal'),
    'unlicense': ('The Unlicense', 'cal'),
    'wtfpl': ('"Do What The F*ck You Want To Public License"', 'cal'),
    'zlib': ('zlib License', 'cal')
}


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
        subdirectories = [
            (os.path.basename(where), True, PACKAGE_SUBDIRECTORIES)
        ]
        init_package(where, args.git, subdirectories)
    if args.license.lower() != 'none':
        create_license(where, args.license, args.git)


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
def create_license(where, license, git=False):
    """
    add preferred LICENSE file
    """
    logger = logging.getLogger(sys._getframe().f_code.co_name)
    fn = 'LICENSE'
    title, vocab = LICENSES[license]
    url = (LICENSE_FIXES[vocab]['prefix'] + license +
           LICENSE_FIXES[vocab]['suffix'])
    targets = [(url, os.path.join(where, fn))]
    fetch(targets, strip_yaml=True)
    if git:
        git_it(where, fn, 'assigned the {0} using text from: {1}'
               ''.format(title, url))
        logger.info('instantiated and committed {0} using {1} from '
                    '{2}'.format(fn, title, url))
    else:
        logger.info('instantiated {0} using {0} from {1}'.format(fn, title,
                                                                 url))


@arglogger
def create_readme(where, git=False):
    """
    create an initial readme file
    """
    logger = logging.getLogger(sys._getframe().f_code.co_name)
    src = TEMPLATES['readme']
    src = os.path.expanduser(src)
    src = os.path.abspath(src)
    dest_fn = os.path.basename(src)
    dest = os.path.join(where, dest_fn)
    shutil.copy2(src, dest)
    logger.debug('copied {0} to {1}'.format(src, dest))
    if git:
        git_it(os.path.dirname(dest), dest_fn,
               'include default readme template')
        logger.info('instantiated {0} and committed it'.format(dest_fn))
    else:
        logger.info('instantiated {0}'.format(dest_fn))


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
    logger.info('instantiated python {0} virtual environment at {1}'
                ''.format(python_version, env_dir))


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
    fp = os.path.join(where, '.gitignore')
    targets = [(url, fp)
               for url in GITIGNORE_URLS]
    fetch(targets)
    with open(fp, 'a') as f:
        f.write('*.bak')
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
    dest = os.path.join(where, dest_fn)
    shutil.copy2(src, dest)
    logger.debug('copied {0} to {1}'.format(src, dest))
    if git:
        git_it(os.path.dirname(dest), dest_fn,
               'include default script template')
    logger.info('added script template as {0}'.format(dest_fn))


@arglogger
def init_package(where, git=False, subdirectories=[]):
    """
    set up as a python package
    """
    logger = logging.getLogger(sys._getframe().f_code.co_name)
    # stub out files using external templates
    targets = [(url, os.path.join(where, url.rsplit('/', 1)[-1]))
               for url in PACKAGE_URLS]
    fetch(targets)
    for target in targets:
        fn = os.path.basename(target[1])
        if git:
            git_it(where, fn, 'intial content for {0} from: {1}'
                   ''.format(target[1], target[0]))
            logger.info('instantiated {0} and committed it'.format(fn))
        else:
            logger.info('instantiated {0}'.format(fn))
    # stub out additional files using internal templates
    templates = []
    templates.append(TEMPLATES['requirements'])
    for template in templates:
        src = os.path.expanduser(template)
        src = os.path.abspath(src)
        dest_fn = os.path.basename(src)
        dest = os.path.join(where, dest_fn)
        shutil.copy2(src, dest)
        logger.debug('copied {0} to {1}'.format(src, dest))
        if git:
            git_it(os.path.dirname(dest), dest_fn,
                   'include default {0} template'.format(dest_fn))
            logger.info('instantiated {0} and committed it'.format(dest_fn))
        else:
            logger.info('instantiated {0}'.format(dest_fn))
    # create subordinate folders
    logger.debug(subdirectories)
    for sub_dir in subdirectories:
        make_subdir(where, git, *sub_dir)


@arglogger
def make_subdir(where, git, dname, init, children):
    """
    create a subdirectory
    """
    logger = logging.getLogger(sys._getframe().f_code.co_name)
    target = os.path.join(where, dname)
    logger.debug('trying to make "{0}"'.format(target))
    try:
        os.makedirs(target)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(where):
            logger.critical(
                'script run with directory creation, but {0} already exists'
                ''.format(target))
            sys.exit(1)
    if init:
        fn = '__init__.py'
        fp = os.path.join(target, fn)
        with open(fp, 'w'):
            pass
        if git:
            git_it(target, fn, 'make {0} part of the package by adding '
                   '__init__.py'.format(target))
            logger.info('instantiated {0} and committed it'.format(fp))
        else:
            logger.info('instantiated {0}'.format(fp))
    for child in children:
        make_subdir(target, git, *child)


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


def fetch(targets, strip_yaml=False):
    """
    fetch file(s) from url(s), concatenate, and save locally
    """
    logger = logging.getLogger(sys._getframe().f_code.co_name)
    for target in targets:
        logger.debug('requesting {0}'.format(target[0]))
        r = requests.get(target[0], stream=True)
        if r.status_code == 200:
            # appending ensures we can aggregate, e.g., .gitignore content
            with open('{0}'.format(target[1]), 'ab') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        else:
            raise Exception('fetch of {0} failed with status code {1}'
                            ''.format([0], r.status_code))
            sys.exit(1)
        logger.debug('successfully saved {0} as {1}'.format(*target))
    if strip_yaml:
        for target in targets:
            fp = target[1]
            post = frontmatter.load(fp)
            shutil.copy(fp, os.path.splitext(fp)[0] + '.bak')
            with open(fp, 'w') as f:
                f.write(post.content)
            logger.debug('removed yaml front matter from {0}'.format(fp))


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
