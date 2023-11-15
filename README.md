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
