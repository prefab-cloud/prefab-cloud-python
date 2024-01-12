class MultiProcessor:
    def __init__(self, processors):
        self.processors = processors

    def __call__(self, logger, method_name, event_dict):
        for processor in self.processors:
            event_dict = processor(logger, method_name, event_dict)
        return event_dict
