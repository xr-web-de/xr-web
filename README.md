xr_web dev instructions
=======================
XR website project based on Django.

Initial setup
-------------
The project runs with _python 3.6_, python packages are managed by _pip_
and installed in a _virtualenv_. Javascript packages are managed by
and installed with _yarn_. And of course this repo uses _git_.

Make sure you have the above dependencies installed, then

### clone the repo

```
# clone the repository
git clone git@github.com:xr-web-de/xr-web.git

# or use HTTPS if you don't have a ssh configured
git clone https://github.com/xr-web-de/xr-web.git

# change directory to repository root
cd xr-web
```

### setup the project

```
# create a virtualenv and activate it
virtualenv -p python3 env
source env/bin/activate

# install python requirements
pip install -r requirements.txt
pip install -r requirements-dev.txt

# install node requirements
yarn install

# setup pre-commit
pre-commit install

# create your local django config
echo 'from .dev import *  # noqa' > src/xr_web/settings/local.py

# run django migrations
src/manage.py migrate
```

Running xr_web
--------------
- Compile your assets with `yarn run watch`
(with Hot Module Replacement)
- Start the django server with `src/manage.py runserver`
- Visit `http://localhost:8000`

Contributing
------------
Before you commit changes:
- reformat your python code with _black_: `black path/or/file.py`
- check your Javascript code with _eslint_:
`./node_modules/.bin/eslint path/or/file.js`
- we recommend _pre-commit_, which makes sure makes sure black is run
and JS code is checked before you commit.
- run tests and the linter, like described in the next section.
- now commit and push to a branch != master


Testing & Linting
-----------------
- use `cd src && ./manage.py test --settings=xr_web.settings.test` to run the python tests
- run `./linter` to run the python and javascript linters and check for missing migrations


Deploying xr_web
----------------
- If there were any js or style changes compile the static assets by running
   `yarn run build_production`, add them to git `git add webpack` and commit & push them.
- FIXME add project specific deployment instructions


Setting up Gitlab CI
--------------------
- In gitlab project settings under CI/CD add a secret variable named `SSH_PRIVATE_KEY` that contains a valid deploy key for the project (and possibly the project's dependencies)
