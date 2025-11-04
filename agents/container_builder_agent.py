from pydantic import BaseModel
from pydantic_ai import Agent
import subprocess
import os
from datetime import datetime


class ContainerBuilderConfig(BaseModel):
    """
    Configuration for the Container Builder Agent.

    Attributes:
        dockerfile_path (str): Path to the Dockerfile
        image_name (str): Base name of the image (e.g. "myapp")
        tag (str): Optional image tag (auto-generated if empty)
        github_user (str): GitHub username or organization
        github_token (str): Personal Access Token with `write:packages`
        repo_name (str): Repository name (used for display/logging)
    """
    dockerfile_path: str
    image_name: str
    tag: str = ""
    github_user: str
    github_token: str
    repo_name: str


class ContainerBuilderAgent(Agent):
    """
    AI Agent that builds Docker images and pushes them to GitHub Container Registry (GHCR).
    """

    def __init__(self, config: ContainerBuilderConfig):
        super().__init__()
        self.config = config

        # Auto-generate a tag if not provided
        if not self.config.tag or self.config.tag.lower() == "latest":
            self.config.tag = "v" + datetime.now().strftime("%Y%m%d-%H%M")

    def build_and_push_image(self) -> str:
        """
        Build the Docker image from the Dockerfile and push to GHCR.

        Returns:
            str: The full image reference (ghcr.io/user/image:tag)
        """
        image_full = f"ghcr.io/{self.config.github_user}/{self.config.image_name}:{self.config.tag}"

        print(f"\n?? Building Docker image: {image_full}")
        try:
            subprocess.run([
                "docker", "build", "--no-cache",
                "-t", image_full,
                "-f", self.config.dockerfile_path, "."
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"? Docker build failed: {e}")
            raise

        print("?? Logging in to GitHub Container Registry...")
        login_result = os.system(
            f"echo {self.config.github_token} | docker login ghcr.io -u {self.config.github_user} --password-stdin"
        )
        if login_result != 0:
            raise RuntimeError("? Failed to authenticate to GHCR. Check your token permissions (needs `write:packages`).")

        print("?? Pushing image to GHCR...")
        try:
            subprocess.run(["docker", "push", image_full], check=True)
        except subprocess.CalledProcessError as e:
            print(f"? Failed to push image: {e}")
            raise

        print(f"? Successfully pushed image: {image_full}")
        return image_full

    def run(self) -> str:
        """
        Run the container builder process end-to-end.
        Returns the final image reference for downstream deployment.
        """
        try:
            image_ref = self.build_and_push_image()
            print(f"?? Final image pushed to: {image_ref}")
            return image_ref
        except Exception as e:
            print(f"?? ContainerBuilderAgent failed: {e}")
            raise
