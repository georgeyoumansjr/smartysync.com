# Colossus

[![Build Status](https://travis-ci.com/vitorfs/colossus.svg?branch=master)](https://travis-ci.com/vitorfs/colossus)
[![codecov](https://codecov.io/gh/vitorfs/colossus/branch/master/graph/badge.svg)](https://codecov.io/gh/vitorfs/colossus)
[![Documentation Status](https://readthedocs.org/projects/colossus/badge/?version=latest)](https://colossus.readthedocs.io/en/latest/?badge=latest)

Self-hosted email marketing solution. Compatible with any SMTP email service.

One-click deploy to Heroku:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Screenshots

![Colossus new campaign](https://colossus.readthedocs.io/en/latest/_images/colossus-new-campaign.png)

![Colossus campaigns](https://colossus.readthedocs.io/en/latest/_images/colossus-campaigns.png)

[More Colossus screenshots.](https://colossus.readthedocs.io/en/latest/features.html#screenshots)

## Features

* Create and manage multiple mailing lists;
* Import lists from other providers (csv files or paste email addresses);
* Create reusable email templates;
* Customize sign up pages (subscribe, unsubscribe, thank you page, etc.);
* Default double opt-in for sign ups;
* Schedule email campaign to send on a specific date and time;
* Track email opens and clicks;
* Change link URL after email is sent;
* Reports with geolocation;
* Compatible with Mailgun, SendGrid, Mandrill, or any other SMTP email service.

## Quickstart

If you want to have a quick look or just run the project locally, you can get started by either forking this repository
or just cloning it directly:

```commandline
git clone git@github.com:vitorfs/colossus.git
```

Ideally, create a [virtualenv](https://docs.python-guide.org/dev/virtualenvs/) and install the projects dependencies:

## **Install PYENV**
for Python 3.6.6 Requirement
```commandline
pip install pyenv-win --target %USERPROFILE%\\.pyenv
```
## **Add System Settings**

It's a easy way to use PowerShell here

1. Adding PYENV, PYENV_HOME and PYENV_ROOT to your Environment Variables

   ```pwsh
   [System.Environment]::SetEnvironmentVariable('PYENV',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")

   [System.Environment]::SetEnvironmentVariable('PYENV_ROOT',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")

   [System.Environment]::SetEnvironmentVariable('PYENV_HOME',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")
   ```

2. Now adding the following paths to your USER PATH variable in order to access the pyenv command

   ```pwsh
   [System.Environment]::SetEnvironmentVariable('path', $env:USERPROFILE + "\.pyenv\pyenv-win\bin;" + $env:USERPROFILE + "\.pyenv\pyenv-win\shims;" + [System.Environment]::GetEnvironmentVariable('path', "User"),"User")
   ```
```commandline
pyenv install 3.6.6
```
Set Global or Local based on your choice with repo
```commandline
pyenv local|global 3.6.6
```

```commandline
pip install -r requirements/development.txt
```

Create a local database:

```commandline
python manage.py migrate
```

Start development server:

```commandline
python manage.py runserver
```

Open your browser and access the setup page to create an admin account:

```commandline
http://127.0.0.1:8000/setup/
```

Docker Commands For PostGresql and Rabbit MQ

```commandline
docker run --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword -d postgres
```

```commandline
docker run -d --hostname my-rabbit --name some-rabbit rabbitmq:3
```

PS: Campaign scheduling will not work out-of-the-box. You need to install a message broker and [setup Celery](https://simpleisbetterthancomplex.com/tutorial/2017/08/20/how-to-use-celery-with-django.html) properly.

## Tech Specs

* Python 3.6
* Django 2.1
* PostgreSQL 10
* Celery 4.2
* RabbitMQ 3.7
* Bootstrap 4 
* jQuery 3.3

PostgreSQL and RabbitMQ are soft dependencies. Other databases (supported by Django) can easily be used as well as other 
message broker compatible with Celery.

The jQuery library is more of a Bootstrap dependency. There is very little JavaScript code in the project. For the most 
part the code base is just plain Django and HTML templates. 

Complete list of Python dependencies can be found in the requirements files.

## Documentation

This is just a pre-release of the project and I still have to work on a proper documentation and user guides.

For now you will only find documentation of the internal APIs in the source code.

[colossus.readthedocs.io](https://colossus.readthedocs.io)

## Who's using Colossus?

Right now just myself. I'm currently using it for my blog newsletter at [simpleisbetterthancomplex.com](https://simpleisbetterthancomplex.com/).

Here is how my sign up page looks like: [sibt.co/newsletter](https://sibt.co/newsletter)

## License

The source code is released under the [MIT License](https://github.com/vitorfs/colossus/blob/master/LICENSE).