# Facemash

As shown in The Social Network movie built with Python using the Django Web Framework.

**P.S:** It ranks people using [Glicko-2 Rating System](https://en.wikipedia.org/wiki/Glicko_rating_system).

![Facemash Screenshot](https://image.ibb.co/j42teo/facemash_screenshot.jpg "Facemash Screenshot")

### Installation Guide

Clone this repository:

```shell
$ git clone https://github.com/thetruefuss/facemash.git
```

Install requirements:

```shell
$ pip install -r requirements.txt
```

Copy `.env.example` file content to new `.env` file and update the credentials if any.

Run Django migrations to create database tables:

```shell
$ python manage.py migrate
```

Run the development server:

```shell
$ python manage.py runserver
```

Verify the deployment by navigating to [http://127.0.0.1:8000](http://127.0.0.1:8000) in your preferred browser.
