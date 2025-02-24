from typing import Optional, Union
from datetime import timedelta

NoDefaultProvided = object()
ConfigValueType = Optional[Union[int, float, bool, str, list[str], timedelta, dict]]
ContextDictType = dict[str, dict[str, ConfigValueType]]
