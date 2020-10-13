# Edurange_Refactored [![license](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)](https://github.com/coojac09/edurange-flask/blob/master/LICENSE) [![Py2&3](https://img.shields.io/badge/Python-2%20%26%203-green.svg)]()

EDURange

Documentation can be found [here](https://github.com/edurange/edurange-flask-docs "EDURange Refactored Documentation")

## Installation
We recommend running on a clean ubuntu or debian instance.
First, clone this repository

```bash
git clone https://github.com/edurange/edurange-flask.git
```

Next, change directory, copy the '.env.example' file to '.env' and edit it where marked
```bash
cd edurange-flask
cp .env.example .env
vim .env
```

Then, run the installation script, and first time npm-build
```bash
chmod +x install.sh
./install.sh
npm run build
```
To verify that you're ready to launch the app, check that "flask" and "celery" are recognized bash commands, and whether "docker run hello-world" works.
If any of these fail, simply log out and back in, and they should work then. 

### Running Locally

Once installed, start the app using
```bash
npm start
```
Or each service can be run separately 
```bash
flask run --host=0.0.0.0
celery worker -B -E -f celery.log -l DEBUG -A edurange_refactored.tasks
```
If you want to host the app on port 80, but don't have any WSGI set up, you can use the following iptables rules
```bash
sudo iptables -t nat -A OUTPUT -o lo -p tcp --dport 80 -j REDIRECT --to-port 5000
sudo iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 -j REDIRECT --to-port 5000
```

#### Database Upkeep

If at any point there are updates to this application that require database schema changes, you can use these commands to update

```bash
flask db init
flask db migrate
flask db upgrade
```
If you will deploy your application remotely (e.g on Heroku) you should add the `migrations` folder to version control.

Make sure folder `migrations/versions` is not empty.

## Debug Settings

Debugging settings can be enabled by editing these values in the '.env' file

```bash
FLASK_ENV=debug
FLASK_DEBUG=1
npm run build   # build assets with webpack
flask run       # start the flask server
```

## Shell

To open the interactive shell, run

```bash
flask shell
```

By default, you will have access to the flask `app`.

## Running Tests/Linter

To run all tests, run

```bash
flask test
```

To run the linter, run

```bash
flask lint
```

The `lint` command will attempt to fix any linting/style errors in the code. If you only want to know if the code will pass CI and do not wish for the linter to make changes, add the `--check` argument.


## Asset Management

Files placed inside the `assets` directory and its subdirectories
(excluding `js` and `css`) will be copied by webpack's
`file-loader` into the `static/build` directory. In production, the plugin
`Flask-Static-Digest` zips the webpack content and tags them with a MD5 hash.
As a result, you must use the `static_url_for` function when including static content,
as it resolves the correct file name, including the MD5 hash.
For example

```html
<link rel="shortcut icon" href="{{static_url_for('static', filename='build/img/favicon.ico') }}">
```

If all of your static files are managed this way, then their filenames will change whenever their
contents do, and you can ask Flask to tell web browsers that they
should cache all your assets forever by including the following line
in ``.env``:

```text
SEND_FILE_MAX_AGE_DEFAULT=31556926  # one year
```
