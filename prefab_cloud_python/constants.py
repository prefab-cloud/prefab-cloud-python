from typing import Optional, Union

NoDefaultProvided = object()
ConfigValueType = Optional[Union[int, float, bool, str, list[str]]]
ContextDictType = dict[str, dict[str, ConfigValueType]]
