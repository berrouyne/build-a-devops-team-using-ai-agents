from pydantic import BaseModel
from pydantic_ai import Agent
import os
import subprocess
import yaml


class KubernetesDeploymentConfig(BaseModel):
    app_name: str = "myapp"
    image_name: str = "myapp:latest"
    replicas: int = 1
    container_port: int = 80
    service_port: int = 80
    namespace: str = "default"
    auto_apply: bool = True


class KubernetesDeploymentAgent(Agent):
    """
    AI Agent that automatically generates and optionally applies Kubernetes manifests
    based on the latest Docker image built by the DevOps AI team.
    """

    def __init__(self, config: KubernetesDeploymentConfig):
        super().__init__()
        self.config = config

    def generate_manifests(self):
        """Generate Kubernetes deployment and service YAMLs dynamically."""
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": self.config.app_name, "namespace": self.config.namespace},
            "spec": {
                "replicas": self.config.replicas,
                "selector": {"matchLabels": {"app": self.config.app_name}},
                "template": {
                    "metadata": {"labels": {"app": self.config.app_name}},
                    "spec": {
                        "containers": [{
                            "name": self.config.app_name,
                            "image": self.config.image_name,  # dynamic image
                            "ports": [{"containerPort": self.config.container_port}]
                        }]
                    }
                }
            }
        }

        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": f"{self.config.app_name}-svc", "namespace": self.config.namespace},
            "spec": {
                "selector": {"app": self.config.app_name},
                "ports": [{
                    "protocol": "TCP",
                    "port": self.config.service_port,
                    "targetPort": self.config.container_port
                }],
                "type": "NodePort"  # easier to access on VPS
            }
        }

        os.makedirs("k8s", exist_ok=True)
        with open("k8s/deployment.yaml", "w") as f:
            yaml.dump(deployment, f, sort_keys=False)
        with open("k8s/service.yaml", "w") as f:
            yaml.dump(service, f, sort_keys=False)
        print("?? Kubernetes manifests generated in ./k8s/")
        return "k8s/deployment.yaml", "k8s/service.yaml"

    def apply_manifests(self):
        """Apply the generated manifests and trigger automatic restart."""
        try:
            subprocess.run(["kubectl", "apply", "-f", "k8s/"], check=True)
            print("? Application deployed successfully to Kubernetes cluster.")

            # ?? Auto-restart deployment to pull new image version
            subprocess.run(
                ["kubectl", "rollout", "restart", f"deployment/{self.config.app_name}"],
                check=True
            )
            print(f"?? Deployment {self.config.app_name} restarted successfully.")

        except subprocess.CalledProcessError as e:
            print(f"? Deployment failed: {e}")

    def run(self):
        """Generate manifests, apply them, and auto-restart deployment."""
        self.generate_manifests()
        if self.config.auto_apply:
            self.apply_manifests()
