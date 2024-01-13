# prefab-cloud-python

Python client for prefab.cloud, providing Config, FeatureFlags as a Service

**Note: This library is under active development**

[Sign up to be notified about updates](https://forms.gle/2qsjMFvjGnkTnA9T8)

## Example usage

```python
from prefab_cloud_python import Client, Options

options = Options(
    prefab_api_key="your-prefab-api-key"
)

context = {
  "user": {
    "team_id": 432,
    "id": 123,
    "subscription_level": 'pro',
    "email": "alice@example.com"
  }
}

client = Client(options)

result = client.enabled("my-first-feature-flag", context=context)

print("my-first-feature-flag is:", result)
```

See full documentation https://docs.prefab.cloud/docs/sdks/python

## Development

1. Ensure that `poetry` is installed: https://python-poetry.org/docs/#installation
2. From the root of this directory, run `poetry install` to ensure dependencies are installed
3. `poetry run python` to open a Python REPL with access to the project dependencies

### Running tests

To run all tests, including integration tests

```bash
poetry run pytest tests
```

To run only local tests and skip integration tests

```bash
poetry run pytest tests -k "not integration"
```

To run only one specific test file

```bash
poetry run pytest tests/name_of_test_file.py
```
