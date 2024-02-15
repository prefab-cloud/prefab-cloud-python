## Gunicorn

This example demonstrates support for gunicorn's forking worker model

`poetry install --no-root`

`poetry PREFAB_API_KEY=XXXXXXXX gunicorn -w 2 -c gunicorn_conf.py myapp:app`

`http -v http://localhost:8000`

### gunicorn_conf.py

Demonstrates resetting the prefab client in the `post_worker_init` hook

### test_app.py

A simple get endpoint that will output the value of a config variable, demonstrating that live updates still work after the worker has forked
