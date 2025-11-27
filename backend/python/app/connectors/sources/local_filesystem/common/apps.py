from app.config.constants.arangodb import AppGroups, Connectors
from app.connectors.core.interfaces.connector.apps import App


class LocalFilesystemApp(App):
    def __init__(self) -> None:
        super().__init__(Connectors.LOCAL_FILESYSTEM.value, AppGroups.LOCAL_FILESYSTEM.value)
