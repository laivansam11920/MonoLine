import re
import time
from uuid import uuid4, UUID
import tempfile
import threading
from pathlib import Path

import git
from flask import Response, g
from git.exc import GitCommandError

from app.core.ai_service import ai
from app.database import db
from app.utils.logger import logger
from configs import Config

__all__ = ["git_services"]


class GitServices:
    def __init__(self):
        self.token: str = Config.GITHUB_USER_TOKEN
        self.name: str = Config.GITHUB_USERNAME
        self.repo_url: str = (
            f"https://{self.token}@github.com/{self.name}/{self.name}.git"
        )

    def git_auto(self):

        try:
            ai_text = ai.get_response()
        except Exception as e:
            logger.error(e)
            ai_text = Config.RES_DEFAULT

        id_commit: UUID = uuid4()

        with tempfile.TemporaryDirectory(prefix="monoline_") as local_dir:

            file_path: Path = Path(local_dir) / "README.md"

            try:

                repo = git.Repo.clone_from(self.repo_url, local_dir)

                if not file_path.is_file():
                    logger.warning(f"README.md not found at {file_path}")
                    return False, None, None

                repo.git.config("user.name", self.name)
                repo.git.config("user.email", f"{self.name}@bot.monoline.com")

                content = file_path.read_text(encoding="utf-8")

                new_content, change_num = re.subn(
                    r"<!--start-->.*?<!--end-->",
                    lambda _: f"<!--start-->\n{ai_text}\n<!--end-->",
                    content,
                    flags=re.DOTALL,
                )

                if change_num == 0:
                    logger.warning(
                        "Could not find <!--start--> or <!--end--> tags in README.md"
                    )
                    return False, None, None

                file_path.write_text(new_content, encoding="utf-8")

                repo.index.add(["README.md"])
                repo.index.commit(f"Id: {id_commit}")

                repo.remote(name="origin").push()

                logger.info(f"Successfully pushed commit ID: {id_commit}")
                return True, id_commit, ai_text
            except GitCommandError as git_err:
                safe_err: str = str(git_err).replace(self.token, "ghp_github_token")
                logger.error(
                    f"Git operation failed for commit {id_commit}. Details: {safe_err}"
                )
                return False, None, None
            except FileNotFoundError:
                logger.error(f"README.md not found at {file_path}")
                return False, None, None
            except Exception as e:
                logger.error(
                    f"Unexpected error during git auto-update (ID: {id_commit}): {e}"
                )
                return False, None, None


class UpdateGitDB(GitServices):

    @staticmethod
    def _async_insert_log(data: dict):
        try:
            db.ai_res.insert_one(data)
            logger.info(f"Background database record saved for commit ID: {data.get("id_commit")}")
        except Exception as e:
            logger.error(f"Error in background insert log: {e}")

    def main(self) -> Response:
        status, id_commit, ai_text = self.git_auto()
        now = time.time()
        success = False
        try:

            if not status:

                return Response(
                    f"Failed to update repository: Check server logs for details.",
                    mimetype="text/plain",
                    status=500,
                )

            log_data = {
                "username": self.name,
                "id_commit": str(id_commit),
                "message": ai_text,
                "time": now,
            }

            threading.Thread(
                target=UpdateGitDB._async_insert_log, args=(log_data,)
            ).start()

            success = True
            return Response("Done to update text", mimetype="text/plain", status=200)
        except Exception as e:
            success = False
            logger.error(
                f"Internal server error in main process (ID: {id_commit}). Details: {e}"
            )

            return Response(
                "Internal server error during the update process.",
                mimetype="text/plain",
                status=500,
            )
        finally:
            if success:
                db.time_limit.update_one(
                    {"username": self.name},
                    {
                        "$set": {
                            "time_last_update": now,
                            "debug": g.limit_data.get("debug", False),
                        }
                    },
                    upsert=True,
                )


git_services = UpdateGitDB()
