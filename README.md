# HillelHomeTask_pro

Summary
1. Getting to know Flask:
   Program launch;
   The basics of working with the framework;
2. Django:
   Object-Relation Mapping (ORM);
   Template maker;
   Middlewares;
   Class/Function Based Views;
   Forms;
   Signals;
3. Caching:
    Connecting memcached;
    Usage principles based on django;
4. Multithreading and multiprocessing:
    Multithreading;
    What is GIL?;
    Multiprocessing;
5. Data parking
    Types of parsers;
    Introduction to beautifulsoup;
6.Web application deployment:
    Systemd;
    Starting the wsgi server (gunicorn/uwsgi);
    Nginx;
7. Parallelization of tasks:
    Celery;
    Running recurring tasks with celerybeat;
    rabbitmq queue manager;
8. Unit tests:
    Types of testing;
    Rytest;
    The difference with other tools;
9. Django Rest Framework:
    The REST approach;
    Endpoint API implementation;
    Swagger;
10. Docker:
    Running containers;
    Writing docker-compose files;
    Dockerization of the entire infrastructure of the application;
11. Databases:
    Types of requests;
    SQL query basics/syntax;
    Sqlite3, postgres;
12. Writing a web server:
    Git;
    virtualenv;

# celery_sample

simple flask app with celery

`docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:3-management`


**default management creds:**

username: guest

password: guest

`celery -A celery_worker worker --loglevel=INFO --purge --pool=solo`

**Postgress**

https://hub.docker.com/_/postgres/

`docker run --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword -d postgres`

**Migrations**

`alembic init alembic`

`alembic revision -m "first" --autogenerate`

`alembic upgrade head`

**Links**

https://www.psycopg.org/

https://docs.sqlalchemy.org/en/14/core/engines.html

https://stackoverflow.com/questions/43477244/how-to-find-postgresql-uri-for-sqlalchemy-config

https://docs.sqlalchemy.org/en/14/tutorial/engine.html

https://flask.palletsprojects.com/en/2.2.x/patterns/sqlalchemy/

https://alembic.sqlalchemy.org/en/latest/tutorial.html
