# `goliath`

The Goliath project by [AlgorithmWatch](https://algorithmwatch.org/) powering [Unding.de](//unding.de).

This project was initially bootstrapped with [Django-Cookie-Cutter](https://github.com/pydanny/cookiecutter-django) but heavily modified.

## Background

This software was created at the end of 2020 and in the beginning of 2021 and only maintained afterward.
The main idea: People can report pre-defined cases of discrimination to the website via a chat-based form.
We create text based on the form responses and that an email to a responsible organization.
The organization should solve the issue.
We store the whole conversation regarding the case on our website (only visible to the user).
A public dashboard provides insight in which organizations resolve which cases (this was not implemented).
The project was created as an MVP, some features are only implemented roughly (e.g. the email validation should be improved if you continue using the code).
The forms for the cases were created with surveyjs (<https://surveyjs.io/>).
This should enable the non-technical people on the project to create new cases.
However, the surveyjs form has to follow certain standards.
Check out the example files (todo).

## Development setup

Get the code, create .ENV files for local development.

```bash
git clone git@github.com:algorithmwatch/goliath.git
cd goliath
mkdir .envs && cp -r docs/exampleenv .envs/.local/
```

Adjust `.envs/.local` to you needs.
See [docs/exampleenv](./docs/exampleenv).

### VS Code Development Container

We recommend to use [VS Code](https://code.visualstudio.com/) with the [Docker](https://docs.docker.com/get-docker/)-based [VS Code Development Container](https://code.visualstudio.com/docs/remote/containers).

As an alternative, see below in the following section on how to use Docker without VS Code.

To start the development server: Open a new terminal and run `/start`.

To run management commands: Open a new terminal and run `./manage.py $command`, e.g., `./manage.py makemigrations`.

#### Adding new extensions

VS-Code extensions are cached between rebuilds.
If you add a new VS Code extension, you need to remove the named volume `docker-compose -f docker-compose.local.yml down && docker volume rm goliath_goliath_extensions`.
([Read more](https://code.visualstudio.com/docs/remote/containers-advanced#_avoiding-extension-reinstalls-on-container-rebuild))

### Docker-Compose

Install and use [Docker](https://docs.docker.com/get-docker/) with Docker-Compose. [More information.](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally-docker.html)

Start development setup:

```bash
./local.sh
```

Some important Django management comands:

```bash
./local.sh manage makemigrations
./local.sh manage migrate
./local.sh manage createsuperuser
./local.sh manage reset_db
./local.sh manage shell_plus --print-sql
./local.sh manage importsupport
./local.sh manage fakedata
```

### Frontend

[Not supporting IE 11 because of Tailwind v2](https://tailwindcss.com/docs/browser-support), but IE 11 usage is [dropping fast](https://gs.statcounter.com/browser-market-share/desktop/germany/#monthly-201812-202012).

If you add a new npm dependency, delete the volume in order to recreate it.

```bash
docker-compose -f docker-compose.local.yml down
docker volume rm goliath_local_node_modules
```

### Test coverage

To run the tests, check your test coverage, and generate an HTML
coverage report:

```bash
coverage run -m pytest
coverage html
open htmlcov/index.html
```

#### Running tests with py.test

```bash
pytest
```

### Celery

To run a celery worker:

```bash
cd goliath
celery -A config.celery_app worker -l info
```

Please note: For Celery's import magic to work, it is important _where_
the celery commands are run. If you are in the same folder with
_manage.py_, you should be right.

### Viewing sent E-Mail during development

In development, to see emails that are being sent from your application. For that reason local SMTP server
[MailHog](https://github.com/mailhog/MailHog) with a web interface is available as Docker container.

View sent emails at: <http://localhost:8025>

## Production

### Settings via environment varibales

See [docs/exampleenv/.django_prod](./docs/exampleenv/.django_prod).
Also the [cookiecutter docs](http://cookiecutter-django.readthedocs.io/en/latest/settings.html) may help for some settings.

### Deployment

We currently support two different Docker-based ways to deploy Goliath:

- [Docker-Compose](./docs/deployment_docker_compose.md) (originating from Django-Cookie-Cutter)
- [Dokku](./docs/deployment_dokku.md) (_preferred_, self-hosted Heroku)

### Sentry

Setup [Sentry](https://sentry.io) to monitor errors.
Set the `SENTRY_DSN` as environment variable.

### New Relic

Setup [New Relic](https://newrelic.com/) for gerneral APM.
Set the following ENVs.

```
NEW_RELIC_LICENSE_KEY=
NEW_RELIC_APP_NAME=
NEW_RELIC_CONFIG_FILE=
```

### E-Mail services

See [docs/emails_mailjet.md](./docs/emails_mailjet.md) on how to configure [Mailjet](https://www.mailjet.com/).
Right now, we only support Mailjet but we could make any other email service from [django-anymail](https://github.com/anymail/django-anymail) work.

### Staging

In order to test the email receiving, you need to have Goliath deployed somewhere.
So think about creating a seperate `staging` server to test Goliath.
You take all the production settings but customize Goliath via .env files.

## License

Affero General Public License 3.0
