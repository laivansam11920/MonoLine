# 1. Standard Library
import os
import re
import shutil
import time
import uuid
from typing import Literal
import tempfile

# 2. Third-party
import git
from flask import Response
from git.exc import GitCommandError

# 3. Local/Internal
from app.core.ai_service import ai
from app.database.connect_db import db
from app.utils.logger import logger
from configs import Config

class GitServices:
    def __init__(self):
        self.token = Config.GITHUB_USER_TOKEN
        self.name = Config.GITHUB_USERNAME
        self.repo_url = f"https://{self.token}@github.com/{self.name}/{self.name}.git"
        self.email = f"{self.name}@monoline.bot"
        self.id_commit = uuid.uuid4()
        self.local_dir = tempfile.mkdtemp(prefix="monoline_")
        self.file_path = f"{self.local_dir}/README.md"
        self.ai_text = ""

    def __repr__(self) -> str: ...

    def git_auto(self) -> Literal[False] | Literal[True]:
        try:

            self.ai_text = ai.get_response

            repo = git.Repo.clone_from(self.repo_url, self.local_dir)

            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read()

            new_content, change_num = re.subn(
                r"<!--start-->.*?<!--end-->",
                lambda m: f"<!--start-->\n{self.ai_text}\n<!--end-->",
                content,
                flags=re.DOTALL,
            )

            if change_num == 0:
                logger.warning("Could not find <!--start--> or <!--end--> tags in README.md")
                return False

            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            repo.git.config("user.name", self.name)
            repo.git.config("user.email", self.email)

            repo.index.add(["README.md"])
            repo.index.commit(f"Update README from AI - ID: {self.id_commit}")

            origin = repo.remote(name="origin")
            origin.push()

            logger.info(f"Successfully pushed commit ID: {self.id_commit}")
            return True
        except GitCommandError as git_err:
            safe_err: str = str(git_err).replace(self.token, "ghp_github_token")
            logger.error(f"Git operation failed for commit {self.id_commit}. Details: {safe_err}")
            return False
        except FileNotFoundError:
            logger.error(f"README.md not found at {self.file_path}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during git auto-update (ID: {self.id_commit}): {e}")
            return False
        finally:
            if os.path.exists(self.local_dir):
                shutil.rmtree(self.local_dir)

class UpdateGitDB(GitServices):
    def __init__(self):
        super().__init__()
        self.time_collection = db.time_limit
        self.limit_time = Config.TIME_LIMIT

    def __repr__(self) -> str: ...

    def main(self) -> Response:
        try:

            res = (
                self.time_collection.find_one(
                    {"username": self.name},
                    {"_id": 0, "time_last_update": 1, "debug": 1}
                )
                or {}
            )

            last_update: int = res.get("time_last_update", 0)
            time_elapsed: float = time.time() - last_update
            debug_active: bool = res.get("debug", False)

            if time_elapsed < self.limit_time and not debug_active:
                time_left: int = round(self.limit_time - time_elapsed, 2)
                return Response(
                    f"Rate limit exceeded. Please try again in {time_left} seconds",
                    mimetype="text/plain",
                    status=429
                )

            self.time_collection.update_one(
                {"username": self.name},
                {"$set": {
                    "time_last_update": time.time(),
                    "debug": debug_active
                }},
                upsert=True,
            )

            if not self.git_auto():
                return Response(
                    "Failed to update repository: Check server logs for details.",
                    status=500,
                    mimetype="text/plain"
                )

            db.ai_res.insert_one(
                {
                    "username": self.name,
                    "id_commit": str(self.id_commit),
                    "message": self.ai_text,
                    "time": time.time(),
                }
            )

            logger.info(f"Database record saved for commit ID: {self.id_commit}")
            return Response(self.ai_text, status=200, mimetype="text/plain")
        except Exception as e:
            logger.error(f"Internal server error in main process (ID: {self.id_commit}). Details: {e}")
            return Response(
                "Internal server error during the update process.",
                status=500,
                mimetype="text/plain"
            )



main = UpdateGitDB()

__all__ = ["main"]
