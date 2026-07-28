import git
import shutil
import os
from configs import Config
from app.core.ai_service import ai
import uuid
from flask import Response
from app.database.connect_db import db
import time
import re
from typing import Literal


class GitServices:
    def __init__(self):
        self.repo_url = f"https://{Config.GITHUB_USER_TOKEN}@github.com/{Config.GITHUB_USERNAME}/{Config.GITHUB_USERNAME}.git"
        self.local_dir = "./temp"
        self.file_path = f"{self.local_dir}/README.md"
        self.name = Config.GITHUB_USERNAME
        self.email = f"{self.name}@monoline.bot"
        self.id_commit = uuid.uuid4()
        self.ai_text = ai.get_response

    def git_auto(self) -> Literal[False] | Literal[True]:
        try:
            repo = git.Repo.clone_from(self.repo_url, self.local_dir)

            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read()

            new_content, change_num = re.subn(
                r"<!--start--->.*?<!--end--->",
                f"<!--start--->\n{self.ai_text}\n<!--end--->",
                content,
                flags=re.DOTALL,
            )

            if change_num == 0:
                print("Not found <!--start--> or <!--end-->", flush=True)
                return False

            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            repo.git.config("user.name", self.name)
            repo.git.config("user.email", self.email)

            repo.index.add(["README.md"])
            repo.index.commit(f"id: {self.id_commit}")

            origin = repo.remote(name="origin")
            origin.push()

            print(f"success to save push {self.id_commit}", flush=True)
            return True
        except Exception as e:
            print(f"have error: {e} to push id {self.id_commit}")
            return False
        finally:
            if os.path.exists(self.local_dir):
                shutil.rmtree(self.local_dir)

    def main(self) -> Response:
        try:

            time_collection = db.time_limit

            res = (
                time_collection.find_one(
                    {"username": self.name}, {"_id": 0, "time_last_update": 1}
                )
                or {}
            )
            _time_cur = time.time() - res.get("time_last_update", 0)

            if _time_cur < Config.TIME_LIMIT:
                return Response(
                    f"{_time_cur} left until the new update", mimetype="text/plain"
                )

            time_collection.update_one(
                {"username": self.name},
                {"$set": {"time_last_update": time.time()}},
                upsert=True,
            )

            if self.git_auto():
                ...
            else:
                return Response("Error in doc", mimetype="text/plain")

            db.ai_res.insert_one(
                {
                    "username": self.name,
                    "id_commit": str(self.id_commit),
                    "message": self.ai_text,
                    "time": time.time(),
                }
            )

            print(f"success to save id {self.id_commit}", flush=True)
            return Response(self.ai_text, mimetype="text/plain")
        except Exception as e:
            print(f"have error: {e} to save id {self.id_commit}", flush=True)
            return Response("Error in server", mimetype="text/plain")


__all__ = ["GitServices"]
