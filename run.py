from app import create_app
from app.utils.cronjob import my_daily_task, self_ping
from app.extension.ap_scheduler import scheduler
from configs import Config

from threading import Thread

app = create_app()

if Config.RENDER_EXTERNAL_URL:
    Thread(target=self_ping, daemon=True).start()
    scheduler.add_job(my_daily_task, "cron", hour=Config.HOUR, minute=Config.MINUTE)
    scheduler.start()

if __name__ == "__main__":
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
