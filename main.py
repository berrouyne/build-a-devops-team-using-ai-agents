from agents.github_actions_agent import GitHubActionsAgent, GitHubActionsConfig
from agents.dockerfile_agent import DockerfileAgent, DockerfileConfig
from agents.build_predictor_agent import BuildPredictorAgent, BuildPredictorConfig
from agents.build_status_agent import BuildStatusAgent, BuildStatusConfig
from agents.k8s_deployment_agent import KubernetesDeploymentAgent, KubernetesDeploymentConfig
from agents.container_builder_agent import ContainerBuilderAgent, ContainerBuilderConfig

import os
import subprocess
import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def main():
    print("?? DevOps AI Team Starting Up...")

    # 1?? GitHub Actions Pipeline
    print("\n1?? GitHub Actions Agent: Creating CI/CD Pipeline...")
    gha_config = GitHubActionsConfig(
        workflow_name="CI Pipeline",
        python_version="3.13.0",
        run_tests=True,
        groq_api_endpoint=os.getenv("GROQ_API_ENDPOINT"),
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    gha_agent = GitHubActionsAgent(config=gha_config)
    pipeline = gha_agent.generate_pipeline()
    os.makedirs(".github/workflows", exist_ok=True)
    with open(".github/workflows/CI3.yml", "w") as f:
        f.write(pipeline)
    print("? CI/CD Pipeline created!")

    # 2?? Dockerfile
    print("\n2?? Dockerfile Agent: Creating Dockerfile...")
    docker_config = DockerfileConfig(
        base_image="nginx:alpine",
        expose_port=80,
        copy_source="./html",
        work_dir="/usr/share/nginx/html",
        groq_api_endpoint=os.getenv("GROQ_API_ENDPOINT"),
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    docker_agent = DockerfileAgent(config=docker_config)
    dockerfile = docker_agent.generate_dockerfile()
    with open("Dockerfile", "w") as f:
        f.write(dockerfile)
    print("? Dockerfile created!")

    # 3?? Build & Check
    print("\n3?? Build Status Agent: Building Docker image...")
    status_config = BuildStatusConfig(image_tag="myapp:latest")
    status_agent = BuildStatusAgent(config=status_config)
    subprocess.run(["docker", "build", "-t", "myapp:latest", "."], check=True)
    status = status_agent.check_build_status()
    print(f"?? Build Status: {status}")

    # 4?? Predict Build
    print("\n4?? Build Predictor Agent: Analyzing build patterns...")
    predictor_config = BuildPredictorConfig(
        model="llama-3.1-8b-instant",
        groq_api_endpoint=os.getenv("GROQ_API_ENDPOINT"),
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    predictor_agent = BuildPredictorAgent(config=predictor_config)
    build_data = {
        "dockerfile_exists": True,
        "ci_pipeline_exists": True,
        "last_build_status": status,
        "python_version": "3.13.0",
        "dependencies_updated": True
    }
    prediction = predictor_agent.predict_build_failure(build_data)
    print(f"?? Build Prediction: {prediction}")

    print("\n? DevOps AI Team has completed their tasks!")

    # 5?? Container Builder  build & push image with timestamp tag
    print("\n5?? Container Builder Agent: Building and pushing image to GHCR...")
    tag = datetime.datetime.now().strftime("v%Y%m%d-%H%M%S")

    builder_config = ContainerBuilderConfig(
        dockerfile_path="./Dockerfile",
        image_name="myapp",
        tag=tag,
        github_user=os.getenv("GH_USER", "berrouyne"),
        github_token=os.getenv("GH_TOKEN"),
        repo_name="build-a-devops-team-using-ai-agents"
    )

    builder_agent = ContainerBuilderAgent(config=builder_config)
    final_image = builder_agent.run()
    print(f"?? Final image pushed to: {final_image}")

    # 6?? Kubernetes Deployment
    print("\n?? Kubernetes Deployment Agent: Generating manifests and deploying...")
    k8s_config = KubernetesDeploymentConfig(
        app_name="myapp",
        image_name=final_image,  # use the actual tagged image
        replicas=1,
        container_port=80,
        service_port=80,
        namespace="default",
        auto_apply=True
    )
    k8s_agent = KubernetesDeploymentAgent(config=k8s_config)
    k8s_agent.run()


if __name__ == "__main__":
    main()
