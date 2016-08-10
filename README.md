# make-project

By [Tom Elliott](http://www.paregorios.org/), 2016.

This is the Python 3 script I use to set up project working directories on my laptop filesystem. 


## License

This code is my original work, though it was built partly by analyzing, adapting, and refining examples found all over the web. It is distributed under the terms of the Unlicense. See LICENSE file.


## Using It

If you run it like this:

```python make.py -cgsp {/path/to/desired/new/directory}```

You'll get:

 * {Directory} creation
 * Git repository initialized in {directory}
 * Python 3 virtual environment created in ~/Envs/{directory}
 * Python script template copied into {directory}/{directory-name}.py

Note the output of ```python make.py -h```:

```
usage: make.py [-h] [-c] [-ca CLASSAUDIENCE] [-cs CLASSDEVSTATUS]
               [-ct CLASSTOPIC] [-g] [-k] [-ka PKGAUTHOR] [-kd PKGDESCRIPTION]
               [-ke PKGEMAIL] [-kh PKGHOMEPAGE] [-kk PKGKEYWORDS]
               [-kv PKGVERSION] [-l LOGLEVEL] [-n PYVERSION] [-p] [-q] [-r]
               [-s] [-v] [-w] [-x LICENSE]
               where

Make a project directory with associated setup

positional arguments:
  where                 path to desired project directory

optional arguments:
  -h, --help            show this help message and exit
  -c, --create          create directory at indicated path (default: False)
  -ca CLASSAUDIENCE, --classaudience CLASSAUDIENCE
                        intended audience classifier to use in setup.py
                        (default: Developers)
  -cs CLASSDEVSTATUS, --classdevstatus CLASSDEVSTATUS
                        development status classifier to use in setup.py
                        (default: 1 - Planning)
  -ct CLASSTOPIC, --classtopic CLASSTOPIC
                        topic classifier to use in setup.py (default: Change
                        Me)
  -g, --git             create a new git repository (default: False)
  -k, --package         set up as a python package (default: False)
  -ka PKGAUTHOR, --pkgauthor PKGAUTHOR
                        user name to use in setup.py (default: Change Me)
  -kd PKGDESCRIPTION, --pkgdescription PKGDESCRIPTION
                        description to use in setup.py (default: change me)
  -ke PKGEMAIL, --pkgemail PKGEMAIL
                        email address to use in setup.py (default:
                        change@me.org)
  -kh PKGHOMEPAGE, --pkghomepage PKGHOMEPAGE
                        home page to use in setup.py (default:
                        http://change.me)
  -kk PKGKEYWORDS, --pkgkeywords PKGKEYWORDS
                        keywords to use in setup.py (default: "change me",
                        "please change me)
  -kv PKGVERSION, --pkgversion PKGVERSION
                        PEP440 version number to use in setup.py (default:
                        0.1)
  -l LOGLEVEL, --loglevel LOGLEVEL
                        desired logging level (case-insensitive string: DEBUG,
                        INFO, WARNING, or ERROR (default: INFO)
  -n PYVERSION, --pyversion PYVERSION
                        version of python to use in virtual environment
                        (default: 3)
  -p, --pyvenv          create a python virtual environment (default: False)
  -q, --quiet           suppress output (logging level == CRITICAL) (default:
                        False)
  -r, --readme          add a readme file template (default: False)
  -s, --script          set up with a python script (default: False)
  -v, --verbose         verbose output (logging level == INFO) (default:
                        False)
  -w, --veryverbose     very verbose output (logging level == DEBUG) (default:
                        False)
  -x LICENSE, --license LICENSE
                        license to use ("none" is an option) (default:
                        agpl-3.0)
```


## Dependencies

make.py makes a ton of assumptions, to include:

 * Mac OSX 10.11.6
 * Predominantly Python development, using a setup more-or-less like that described by Justin Mayer in  [‘Python Development Environment on Mac OS X Yosemite 10.10’, *Hacker Codex,* 2015](http://hackercodex.com/guide/python-development-environment-on-mac-osx/), especially Python 2, Python 3, and git installed with [*Homebrew*](http://brew.sh/).
 * [Doug Hellman's *virtualenvwrapper*](http://virtualenvwrapper.readthedocs.io/en/latest/) installed with *Homebrew*.
 * Access to the Internet at runtime

The only non-standard Python packages used are:

 * [*Requests*](http://docs.python-requests.org/en/master/).
 * [*Python Frontmatter*](https://github.com/eyeseast/python-frontmatter)

Current code makes use of the following external resources as templates or defaults:

 * Standard package files (like setup.py) from the [Python Packaging Authority's sample project respository](https://github.com/pypa/sampleproject)
 * .gitignore content for OSX and Python from [GitHub's gitignore templates repository](https://github.com/github/gitignore)
 * License text files from [GitHub's choosealicense.com repository](https://github.com/github/choosealicense.com) and elsewhere as necessary


## Development

I might do more work on this at some point, hence the following to-do list:

 * Fold package templates into this repos
 * Config file support
 * Non-hard-coded directory and file references
 * provide requirements and stuff so config to run this script is easier

Forking is encouraged. Pull requests containing new or improved features are welcome (including items on the to-do list). They are likely to be merged unless they break something that works for me now or they add stuff I don't need that can't be turned off. Bug reports will be reviewed, but will be closed "won't fix" unless they're occurring on my machine. If you provide a patch or pull request with the bug report, and it doesn't break stuff that's working for me, I will probably merge it. Responsiveness timescales may vary wildly.





