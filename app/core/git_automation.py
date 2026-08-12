# 1. Standard Library
import os
import re
import shutil
import time
from uuid import uuid4, UUID
from typing import Literal
import tempfile
import threading
from pathlib import Path

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
        self.token: str = Config.GITHUB_USER_TOKEN
        self.name: str = Config.GITHUB_USERNAME
        self.repo_url: str = (
            f"https://{self.token}@github.com/{self.name}/{self.name}.git"
        )
        self.email: str = f"{self.name}@monoline.bot"
        self.id_commit: UUID | int = 0
        self.local_dir: str = tempfile.mkdtemp(prefix="monoline_")
        self.file_path: Path = Path(self.local_dir) / "README.md"
        self.ai_text: str = ""

    def __repr__(self) -> str: ...

    def git_auto(self) -> Literal[False] | Literal[True]:
        try:

            repo = git.Repo.clone_from(self.repo_url, self.local_dir)

            if not self.file_path.is_file():
                logger.warning(f"README.md not found at {self.file_path}")
                return False

            repo.git.config("user.name", self.name)
            repo.git.config("user.email", self.email)

            self.ai_text = ai.get_response()

            content = self.file_path.read_text(encoding="utf-8")

            new_content, change_num = re.subn(
                r"<!--start-->.*?<!--end-->",
                lambda m: f"<!--start-->\n{self.ai_text}\n<!--end-->",
                content,
                flags=re.DOTALL,
            )

            if change_num == 0:
                logger.warning(
                    "Could not find <!--start--> or <!--end--> tags in README.md"
                )
                return False

            self.file_path.write_text(new_content, encoding="utf-8")

            repo.index.add(["README.md"])
            self.id_commit = uuid4()
            repo.index.commit(f"Update README from AI - ID: {self.id_commit}")

            origin = repo.remote(name="origin")
            origin.push()

            logger.info(f"Successfully pushed commit ID: {self.id_commit}")
            return True
        except GitCommandError as git_err:
            safe_err: str = str(git_err).replace(self.token, "ghp_github_token")
            logger.error(
                f"Git operation failed for commit {self.id_commit}. Details: {safe_err}"
            )
            return False
        except FileNotFoundError:
            logger.error(f"README.md not found at {self.file_path}")
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error during git auto-update (ID: {self.id_commit}): {e}"
            )
            return False
        finally:
            if os.path.exists(self.local_dir):
                shutil.rmtree(self.local_dir)


class UpdateGitDB(GitServices):
    def __init__(self):
        super().__init__()
        self.time_collection = db.time_limit
        self.time: float | int = 0
        self.debug_active = None
        self.success: bool = False

    def __repr__(self) -> str: ...

    def _async_insert_log(self, data):
        try:
            db.ai_res.insert_one(data)
            logger.info(
                f"Background database record saved for commit ID: {self.id_commit}"
            )
        except Exception as e:
            logger.error(f"Error in background insert log: {e}")

    def main(self) -> Response:
        try:

            self.time = time.time()
            time_res_db = (
                self.time_collection.find_one(
                    {"username": self.name}, {"_id": 0, "debug": 1}
                )
                or {}
            )
            self.debug_active: bool = time_res_db.get("debug", False)

            if not self.git_auto():

                return Response(
                    f"Failed to update repository: Check server logs for details.",
                    mimetype="text/plain",
                    status=500,
                )

            log_data = {
                "username": self.name,
                "id_commit": str(self.id_commit),
                "message": self.ai_text,
                "time": self.time,
            }

            threading.Thread(target=self._async_insert_log, args=(log_data,)).start()

            self.success = True
            return Response("Done to update text", mimetype="text/plain", status=200)
        except Exception as e:
            self.success = False
            logger.error(
                f"Internal server error in main process (ID: {self.id_commit}). Details: {e}"
            )

            return Response(
                "Internal server error during the update process.",
                mimetype="text/plain",
                status=500,
            )
        finally:
            if self.success:
                self.time_collection.update_one(
                    {"username": self.name},
                    {
                        "$set": {
                            "time_last_update": self.time,
                            "debug": self.debug_active,
                        }
                    },
                    upsert=True,
                )


main = UpdateGitDB()

__all__ = ["main"]
