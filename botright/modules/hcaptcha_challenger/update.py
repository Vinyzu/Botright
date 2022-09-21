import os.path

import httpx

from .solutions.kernel import Solutions
from .settings import DIR_MODEL, PATH_OBJECTS_YAML

def update_ai():
    # Updating Objects.yaml file
    objects = httpx.get("https://raw.githubusercontent.com/QIN2DIM/hcaptcha-challenger/main/src/objects.yaml").text
    with open(PATH_OBJECTS_YAML, "w", encoding="utf-8") as f:
        f.write(objects)

    # Dowloading ONNX files
    release = httpx.get("https://api.github.com/repos/QIN2DIM/hcaptcha-challenger/releases/latest").json()

    for asset in release["assets"]:
        url = asset["browser_download_url"]
        name = asset["name"]
        model_path = os.path.join(DIR_MODEL, name)
        if not os.path.isfile(model_path):
            Solutions.download_model_(DIR_MODEL, model_path, url, name)