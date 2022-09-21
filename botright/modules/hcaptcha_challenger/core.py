from typing import Optional

from .exceptions import ChallengeLangException
from .solutions import resnet, sk_recognition, yolo


class ArmorCaptcha:
    """hCAPTCHA challenge drive control"""

    label_alias = {
        "zh": {
            "自行车": "bicycle",
            "火车": "train",
            "卡车": "truck",
            "公交车": "bus",
            "巴士": "bus",
            "飞机": "airplane",
            "一条船": "boat",
            "船": "boat",
            "摩托车": "motorcycle",
            "垂直河流": "vertical river",
            "天空中向左飞行的飞机": "airplane in the sky flying left",
            "请选择天空中所有向右飞行的飞机": "airplanes in the sky that are flying to the right",
            "汽车": "car",
            "大象": "elephant",
            "鸟": "bird",
            "狗": "dog",
            "犬科动物": "dog",
            "一匹马": "horse",
            "长颈鹿": "giraffe",
        },
        "en": {
            "airplane": "airplane",
            "motorbus": "bus",
            "bus": "bus",
            "truck": "truck",
            "motorcycle": "motorcycle",
            "boat": "boat",
            "bicycle": "bicycle",
            "train": "train",
            "vertical river": "vertical river",
            "airplane in the sky flying left": "airplane in the sky flying left",
            "Please select all airplanes in the sky that are flying to the right": "airplanes in the sky that are flying to the right",
            "car": "car",
            "elephant": "elephant",
            "bird": "bird",
            "dog": "dog",
            "canine": "dog",
            "horse": "horse",
            "giraffe": "giraffe",
        },
    }

    BAD_CODE = {
        "а": "a",
        "е": "e",
        "e": "e",
        "i": "i",
        "і": "i",
        "ο": "o",
        "с": "c",
        "ԁ": "d",
        "ѕ": "s",
    }

    HOOK_CHALLENGE = "//iframe[contains(@title,'content')]"

    # <success> Challenge Passed by following the expected
    CHALLENGE_SUCCESS = "success"
    # <continue> Continue the challenge
    CHALLENGE_CONTINUE = "continue"
    # <crash> Failure of the challenge as expected
    CHALLENGE_CRASH = "crash"
    # <retry> Your proxy IP may have been flagged
    CHALLENGE_RETRY = "retry"
    # <refresh> Skip the specified label as expected
    CHALLENGE_REFRESH = "refresh"
    # <backcall> (New Challenge) Types of challenges not yet scheduled
    CHALLENGE_BACKCALL = "backcall"

    def __init__(
        self,
        dir_workspace: str = None,
        lang: Optional[str] = "zh",
        dir_model: str = None,
        onnx_prefix: str = None,
        screenshot: Optional[bool] = False,
        debug=False,
        path_objects_yaml: Optional[str] = None,
        path_rainbow_yaml: Optional[str] = None,
    ):
        if not isinstance(lang, str) or not self.label_alias.get(lang):
            raise ChallengeLangException(
                f"Challenge language [{lang}] not yet supported."
                f" -lang={list(self.label_alias.keys())}"
            )

        self.action_name = "ArmorCaptcha"
        self.debug = debug
        self.dir_model = dir_model
        self.onnx_prefix = onnx_prefix
        self.screenshot = screenshot
        self.path_objects_yaml = path_objects_yaml
        self.path_rainbow_yaml = path_rainbow_yaml

        # 存储挑战图片的目录
        self.runtime_workspace = ""
        # 挑战截图存储路径
        self.path_screenshot = ""
        # 博大精深！
        self.lang = lang
        self.label_alias: dict = self.label_alias[lang]

        # Store the `element locator` of challenge images {挑战图片1: locator1, ...}
        self.alias2locator = {}
        # Store the `download link` of the challenge image {挑战图片1: url1, ...}
        self.alias2url = {}
        # Store the `directory` of challenge image {挑战图片1: "/images/挑战图片1.png", ...}
        self.alias2path = {}
        # 图像标签
        self.label = ""
        self.prompt = ""
        # 运行缓存
        self.dir_workspace = dir_workspace if dir_workspace else "."

        self.threat = 0

        # Automatic registration
        self.pom_handler = resnet.PluggableONNXModels(self.path_objects_yaml)
        self.label_alias.update(self.pom_handler.label_alias[lang])
        self.pluggable_onnx_models = self.pom_handler.overload(
            self.dir_model, path_rainbow=self.path_rainbow_yaml
        )
        self.yolo_model = yolo.YOLO(self.dir_model, self.onnx_prefix)

    def switch_solution(self):
        """Optimizing solutions based on different challenge labels"""
        sk_solution = {
            "vertical river": sk_recognition.VerticalRiverRecognition,
            "airplane in the sky flying left": sk_recognition.LeftPlaneRecognition,
            "airplanes in the sky that are flying to the right": sk_recognition.RightPlaneRecognition,
        }

        label_alias = self.label_alias.get(self.label)

        # Select ResNet ONNX model
        if self.pluggable_onnx_models.get(label_alias):
            return self.pluggable_onnx_models[label_alias]
        # Select SK-Image method
        if sk_solution.get(label_alias):
            return sk_solution[label_alias](self.path_rainbow_yaml)
        # Select YOLO ONNX model
        return self.yolo_model
