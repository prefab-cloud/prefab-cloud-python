from abc import ABC, abstractmethod
import prefab_pb2 as Prefab


class ConfigClientInterface(ABC):
    @abstractmethod
    def continue_connection_processing(self) -> bool:
        pass

    @abstractmethod
    def highwater_mark(self) -> str:
        pass

    @abstractmethod
    def handle_unauthorized_response(self) -> None:
        pass

    @abstractmethod
    def is_shutting_down(self) -> bool:
        pass

    @abstractmethod
    def load_configs(self, configs: Prefab.Configs, src: str) -> None:
        pass

    @property
    @abstractmethod
    def options(self):
        pass
