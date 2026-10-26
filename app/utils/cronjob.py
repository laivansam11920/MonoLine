from time import sleep
from requests import get

from configs import Config
from app.core.git_automation import get_git_services, UpdateGitDB
from app.utils.logger import logger
from app.database import Database


def self_ping():
    sleep(10)
    while True:
        if Config.RENDER_EXTERNAL_URL:
            try:
                get(f"{Config.RENDER_EXTERNAL_URL}/ping", timeout=10)
            except Exception as e:
                logger.error(e)
        sleep(10 * 60)

@Database.del_document
def my_daily_task():
    try:
        git_services: UpdateGitDB = get_git_services()
        git_services.main()
    except Exception as e:
        logger.error(e)
