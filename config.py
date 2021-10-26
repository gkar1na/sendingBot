from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """ Instance stores all app settings, mainly environment variables """
    PROJECT_NAME: str = 'MovementAcademy'

    VK_BOT_TOKEN: Optional[str]

    STEPS: Optional[str]
    COMMANDS: Optional[str]
    TEXTS: Optional[str]

    MY_VK_ID: Optional[int]

    UNREAD_MESSAGE_TEXT: Optional[str]

    DB_PATH: Optional[str]

    DELAY: Optional[float]

    class Config:
        env_prefix = 'MOVEMENT_ACADEMY_'
        env_file = '.env'
        env_file_encoding = 'utf-8'

        # uncomment when testing
        # env_prefix = 'TEST_' + env_prefix


settings = Settings()
