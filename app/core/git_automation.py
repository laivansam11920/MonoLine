import git
import shutil
import os
from configs import Config
from app.core.ai_service import response_text
import uuid
from flask import Response


class GitServices:
    def __init__(self):
        self.repo_url = f"https://{Config.GITHUB_USER_TOKEN}@github.com/{Config.GITHUB_USERNAME}/{Config.GITHUB_USERNAME}.git"
        self.local_dir = "./temp"
        self.file_path = f"{self.local_dir}/README.md"
        self.name = Config.GITHUB_USERNAME
        self.email = f"{self.name}@monoline.com"
        self.id_commit = uuid.uuid4()

    def git_auto(self) -> Response:
        try:
            repo = git.Repo.clone_from(self.repo_url, self.local_dir)

            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(response_text)

            repo.git.config("user.name", self.name)
            repo.git.config("user.email", self.email)

            repo.index.add(["README.md"])
            repo.index.commit(f"id: {self.id_commit}")

            origin = repo.remote(name="origin")
            origin.push()

            print(f"success to save id {self.id_commit}", flush=True)
            return Response(response_text, mimetype="text/plain")
        except Exception as e:
            print(f"have error: {e} to save id {self.id_commit}", flush=True)
            return Response("Error in server", mimetype="text/plain")
        finally:
            if os.path.exists(self.local_dir):
                shutil.rmtree(self.local_dir)


__all__ = ["GitServices"]
