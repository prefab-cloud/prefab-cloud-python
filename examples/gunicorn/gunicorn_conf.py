import logging

import prefab_cloud_python
from prefab_cloud_python import Options

def on_starting(server):
    logging.warning("Starting server")
    prefab_cloud_python.set_options(Options(collect_sync_interval=5))
    logging.warning(f"current value of 'foobar' is {prefab_cloud_python.get_client().get('foobar')}")

def post_worker_init(worker):
    # Initialize the client for each worker
    prefab_cloud_python.reset_instance()

def on_exit(server):
    logging.warning("shutting down prefab")
    prefab_cloud_python.reset_instance()

