import git
import shutil
import os
from configs import Config
from app.core.ai_service import GenAIService

repo_url = f"https://{Config.GITHUB_USER_TOKEN}@github.com/{Config.GITHUB_USERNAME}/{Config.GITHUB_USERNAME}.git"
local_dir = "./temp"

if os.path.exists(local_dir): shutil.rmtree(local_dir)

try:
    repo = git.Repo.clone_from(repo_url, local_dir)
    file_path = f"{local_dir}/README.md"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(GenAIService().get_response())

    repo.index.add(["README.md"])

    repo.git.config("user.name", "Render Bot")
    repo.git.config("user.email", "bot@render.com")

    repo.index.commit("auto")
    origin = repo.remote(name="origin")
    origin.push()

except Exception as e:
    print(e)

