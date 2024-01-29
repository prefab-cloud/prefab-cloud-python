class StructlogMultiProcessor:
    """
    This is a utility to wrap the three prefab structlog processors as just one in your structlog configuration
    It can be instantiated by the create_prefab_structlog_processor method exposed by the prefab_cloud_python module
    use of this is preferred over the individual processors from _structlog_processors.py
    """

    def __init__(self, processors):
        self.processors = processors

    def __call__(self, logger, method_name, event_dict):
        for processor in self.processors:
            event_dict = processor(logger, method_name, event_dict)
        return event_dict
