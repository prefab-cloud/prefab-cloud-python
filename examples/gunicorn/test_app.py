import prefab_cloud_python


def app(environ, start_response):
    output = f"value of 'test.config' is {prefab_cloud_python.get_client().config_client().get('test.config')}".encode()
    start_response(
        "200 OK", [("Content-Type", "text/plain"), ("Content-Length", str(len(output)))]
    )
    return iter([output])
