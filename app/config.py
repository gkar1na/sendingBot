from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """ Instance stores all app settings, mainly environment variables """
    PROJECT_NAME: str = 'ANTIPOSVYAT'

    VK_BOT_TOKEN: Optional[str]
    GROUP_ID: Optional[str]

    STEPS: Optional[str]
    COMMANDS: Optional[str]
    TEXTS: Optional[str]

    MY_VK_ID: Optional[int]

    UNREAD_MESSAGE_TEXT: Optional[str]

    DB_PATH: Optional[str]
    TITLE_WELCOME: Optional[str]

    DELAY: Optional[float]

    GOOGLE_TABLE_PATH: Optional[str]
    GOOGLE_TABLE_PATH2: Optional[str]
    GOOGLE_FOLDER_ID: Optional[str]

    BASIC_BUTTONS: Optional[str]

    class Config:
        env_prefix = 'ANTIPOSVYAT_'
        env_file = r'C:\Users\user\PycharmProjects\sendingBot\app\.env'
        env_file_encoding = 'utf-8'

        #uncomment when testing
        env_prefix = 'TEST_' + env_prefix


settings = Settings()