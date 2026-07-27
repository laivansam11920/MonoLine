import git
import shutil
import os
from configs import Config
from app.core.ai_service import response_text
import uuid
from flask import Response
from app.database.connect_db import db
import time


class GitServices:
    def __init__(self):
        self.repo_url = f"https://{Config.GITHUB_USER_TOKEN}@github.com/{Config.GITHUB_USERNAME}/{Config.GITHUB_USERNAME}.git"
        self.local_dir = "./temp"
        self.file_path = f"{self.local_dir}/README.md"
        self.name = Config.GITHUB_USERNAME
        self.email = f"{self.name}@monoline.bot"
        self.id_commit = uuid.uuid4()

    def git_auto(self) -> Response:
        try:

            res = db.time_limit.find_one({'username': self.name}, {'_id': 0, 'time_last_update': 1}) or {}
            _time = time.time() - res.get("time_last_update", 0)

            if _time < Config.TIME_LIMIT:
                return Response(f'{_time}', mimetype="text/plain")

            db.time_limit.update_one(
                {"username": self.name},
                {"$set": {"time_last_update": time.time()}},
                upsert=True,
            )

            repo = git.Repo.clone_from(self.repo_url, self.local_dir)

            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(response_text)

            repo.git.config("user.name", self.name)
            repo.git.config("user.email", self.email)

            repo.index.add(["README.md"])
            repo.index.commit(f"id: {self.id_commit}")

            origin = repo.remote(name="origin")
            origin.push()

            db.ai_res.insert_one({
                'username': self.name,
                'id_commit': str(self.id_commit),
                'message': response_text,
                'time': time.time(),
            })

            print(f"success to save id {self.id_commit}", flush=True)
            return Response(response_text, mimetype="text/plain")
        except Exception as e:
            print(f"have error: {e} to save id {self.id_commit}", flush=True)
            return Response("Error in server", mimetype="text/plain")
        finally:
            if os.path.exists(self.local_dir):
                shutil.rmtree(self.local_dir)


__all__ = ["GitServices"]
