xr_web
------------------------------------------
XR website project based on Django.


Initial setup
-------------


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
---------------------------------------
- Compile your assets with `yarn run watch`
- Start the django server with `src/manage.py runserver`
- Visit `http://localhost:8000`

Deploying xr_web
---------------------------------------
- If there were any js or style changes compile the static assets by running
   `npm run build_production`, add them to git `git add webpack` and commit & push them.
- FIXME add project specific deployment instructions

Testing & Linting
------------------
- use `cd src && ./manage.py test --settings=xr_web.settings.test` to run the python tests
- run `./linter` to run the python and javascript linters and check for missing migrations

Setting up Gitlab CI
--------------------
- In gitlab project settings under CI/CD add a secret variable named `SSH_PRIVATE_KEY` that contains a valid deploy key for the project (and possibly the project's dependencies)
