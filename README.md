# xr_web dev instructions

XR website project based on Django.

## Initial setup

The project runs with _python 3.6_, python packages are managed by _pip_
and installed in a _virtualenv_. Javascript packages are managed by
and installed with _yarn_. And of course this repo uses _git_.

Make sure you have the above dependencies installed, then

### clone the repo

```
# clone the repository
git clone https://code.organise.earth/xr-web-de/xr-web.git

# change directory to repository root
cd xr-web
```

### setup the project

```
# create a python3 virtualenv and activate it
virtualenv -p python3 env
source env/bin/activate

# install python requirements
pip install -r requirements.txt
pip install -r requirements-dev.txt

# install node requirements
yarn install

# setup pre-commit (recommended)
pre-commit install

# create your local django config
echo 'from .dev import *  # noqa' > src/xr_web/settings/local.py

# run django database migrations
src/manage.py migrate
```

## Running xr_web

-   Compile your assets with `yarn run watch`
    (with Hot Module Replacement)
-   Start the django server with `src/manage.py runserver`
-   Visit [http://localhost:8000](http://localhost:8000)

## Create a (super-)user and log in

-   run `src/manage.py createsuperuser`
-   you find the Wagtail CMS admin at `/admin/`
    ([http://localhost:8000/admin/](http://localhost:8000/admin/))

## Contributing

Checkout the project and create a new branch.
Commit your changes to the new branch.
Create a merge request for your branch.

We merge changes when tests and the linter do not complain.
And of course the changes should be constructive.

In order to satisfy the code styleguide:

-   reformat your python code with _black_: `black ./src`
-   check your Javascript code with _eslint_:
    `./node_modules/.bin/eslint ./src`
-   we recommend _pre-commit_, which makes sure makes sure black is run
    and JS code is checked before you commit.

You can run the tests and linter, as described in the next section.

## Testing & Linting

-   use `cd src && ./manage.py test --settings=xr_web.settings.test` to run the python tests
-   run `./linter` to run the python and javascript linters and check for missing migrations

## Deploying xr_web

-   If there were any js or style changes compile the static assets by running
    `yarn run build_production`, add them to git `git add webpack` and commit & push them.
-   FIXME add project specific deployment instructions

## Setting up Gitlab CI

-   In gitlab project settings under CI/CD add a secret variable named `SSH_PRIVATE_KEY` that contains a valid deploy key for the project (and possibly the project's dependencies)
