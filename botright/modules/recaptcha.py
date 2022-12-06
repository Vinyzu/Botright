# Largely Implemented from https://github.com/QIN2DIM/recaptcha-challenger
import io
import json
import logging
import tempfile

import numpy as np

# Deactivating Pytorch Logging/Warnings
logging.getLogger("utils.general").setLevel(logging.WARNING)
import os

# Deactivating Tensorflow Warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import hcaptcha_challenger as solver
import httpx
import pydub
import yolov5
from PIL import Image, ImageOps
from speech_recognition import AudioFile, Recognizer
from tensorflow import keras

logging.getLogger("yolov5").disabled = True


class AudioCaptcha:
    def parse_audio_to_text(path_audio_wav):
        # Internationalized language format of audio files, default en-US American pronunciation.
        language = "en-US"

        # Read audio into and cut into a frame matrix
        recognizer = Recognizer()
        audio_file = AudioFile(path_audio_wav)
        with audio_file as stream:
            audio = recognizer.record(stream)

        # Returns the text corresponding to the short audio(str)，
        # en-US Several words that are not sentence patterns
        audio_answer = recognizer.recognize_google(audio, language=language)

        return audio_answer

    def handle_audio(audio_url):
        # Splice audio cache file path
        audio_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        audio_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")

        # Download the sound source file to the local
        audio_mp3.write(httpx.get(audio_url).content)

        # Convert audio format mp3 --> wav
        pydub.AudioSegment.from_mp3(audio_mp3.name).export(audio_wav.name, format="wav")

        # Returns audio files in wav format to increase recognition accuracy
        solution = AudioCaptcha.parse_audio_to_text(audio_wav.name)
        return solution

    async def audio_recaptcha(page):
        # Clicking Captcha Checkbox
        try:
            checkbox = page.frame_locator("//iframe[@title='reCAPTCHA']").locator(".recaptcha-checkbox-border")
            await checkbox.click()
        except Exception:
            print("reCaptcha didnt load")
            return False

        try:
            captcha_frame = page.frame_locator("//iframe[contains(@src,'bframe')]")
        except Exception as e:
            captcha_token = await page.evaluate("grecaptcha.getResponse()")
            if captcha_token:
                return captcha_token
            else:
                print("reCaptcha didnt load")
                return False

        switcher = captcha_frame.locator("[id='recaptcha-audio-button']")
        await switcher.click()

        try:
            audio_element = captcha_frame.locator("#audio-source")
            audio_url = await audio_element.get_attribute("src")
        except Exception:
            print("Ratelimited to prevent Botting (Use another IP)")
            return False

        solution = AudioCaptcha.handle_audio(audio_url)

        input_field = captcha_frame.locator("#audio-response")
        await input_field.fill("")
        await input_field.type(solution.lower())
        # Submit answer
        await input_field.press("Enter")

        return await page.evaluate("grecaptcha.getResponse()")


class VisualCaptcha:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    model = keras.models.load_model(f"{dir_path}/recaptcha_model/keras_model.h5", compile=False)
    class_names = open(f"{dir_path}/recaptcha_model/labels.txt", "r").readlines()

    solver.install()
    # Initializing ArmorCaptcha
    challenger = solver.new_challenger(debug=False)
    challenger.label = "bicycle"
    yolo = challenger.switch_solution()

    object_detection_yolo = yolov5.load("yolov5s.pt", device="cpu")

    alias = {"car": "car", "cars": "car", "vehicles": "car", "taxis": "car", "taxi": "car", "bus": "bus", "buses": "bus", "bus": "train", "buses": "train", "motorcycles": "motorcycle", "bicycles": "bicycle", "boats": "boat", "fire hidrants": "fire hydrant", "a fire hydrant": "fire hydrant", "parking meters": "parking meter", "traffic lights": "traffic light"}

    label = ""
    dynamic = False
    latest_captcha = None

    async def custom_ai(image_data):
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

        # Replace this with the path to your image
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        # resize the image to a 224x224 with the same strategy as in TM2:
        # resizing the image to be at least 224x224 and then cropping from the center
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)

        # turn the image into a numpy array
        image_array = np.asarray(image)
        # Normalize the image
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

        # Load the image into the array
        data[0] = normalized_image_array
        # run the inference
        prediction = VisualCaptcha.model.predict(data)

        try:
            good = np.argwhere(prediction > 0.3)[0]
            results = [VisualCaptcha.class_names[index].strip() for index in good]
            return VisualCaptcha.label in results
        except Exception:
            return False

    async def check_positive_element(sample):
        image_data = await sample.screenshot()

        if VisualCaptcha.label in VisualCaptcha.alias:
            result = VisualCaptcha.yolo.solution(img_stream=image_data, label=VisualCaptcha.alias[VisualCaptcha.label], confidence=0.5)
            if result:
                await sample.click()
        else:
            if result := await VisualCaptcha.custom_ai(image_data):
                await sample.click()

        return result

    async def object_detection(captcha_frame, samples):
        captcha_area = captcha_frame.locator('[class="rc-imageselect-challenge"]')
        boundings = await samples.first.bounding_box()
        start_x, start_y, _, _ = boundings.values()

        image_data = await captcha_area.screenshot()

        # Converting the ImageBytes into Pillow
        pil_image = Image.open(io.BytesIO(image_data)).convert("RGB")

        # Inference
        results = VisualCaptcha.object_detection_yolo(pil_image)

        # Processing the Results
        json_string = results.pandas().xyxy[0].to_json(orient="records")
        results = json.loads(json_string)

        coords = []
        for result in results:
            if result["name"] == VisualCaptcha.alias[VisualCaptcha.label]:  # and result["confidence"] > 0.2
                xmin, ymin, xmax, ymax = (int(result["xmin"]), int(result["ymin"]), int(result["xmax"]), int(result["ymax"]))
                coords.append([xmin + int(start_x), ymin + int(start_y), xmax + int(start_x), ymax + int(start_y)])

        already_true = []
        for index in range(await samples.count()):
            sample = samples.nth(index)
            # Getting the Middle Coordinate of the Tile
            boundings = await sample.bounding_box()
            x, y, width, height = boundings.values()
            x, y, width, height = int(x), int(y), int(width), int(height)
            # Checking if the Middle is in the Results
            for coord in coords:
                if any(x in range(coord[0], coord[2]) for x in range(x, x + width)) and any(y in range(coord[1], coord[3]) for y in range(y, y + height)):
                    if not index in already_true:
                        await sample.click()
                        already_true.append(index)

    async def solve_captcha(page, captcha_frame):
        dynamic = False

        samples = captcha_frame.locator("//td[@aria-label]")
        object_detection = await samples.count() > 9
        if object_detection and VisualCaptcha.label not in ("crosswalks", "stairs", "chimneys"):
            await VisualCaptcha.object_detection(captcha_frame, samples)
            return samples

        for index in range(await samples.count()):
            # Using Yolo to determine the answer of the CaptchaSample
            sample = samples.nth(index)
            result = await VisualCaptcha.check_positive_element(sample)

            motion_status = await sample.get_attribute("class")

            if "dynamic" in motion_status:
                dynamic = True

        if dynamic:
            await page.wait_for_timeout(3000)
            await VisualCaptcha.solve_captcha(page, captcha_frame)

        return samples

    async def checkbox(page):
        # Clicking Captcha Checkbox
        try:
            checkbox = page.frame_locator("//iframe[@title='reCAPTCHA']").locator(".recaptcha-checkbox-border")
            await checkbox.click()
        except Exception:
            print("reCaptcha didnt load")
            return False

        await page.wait_for_timeout(1000)

    async def get_first_image(sample):
        # For Checking if the captcha was solved correctly
        image = sample.locator("//img")
        image_url = await image.get_attribute("src")
        return image_url

    async def visual_recaptcha(page, first_time=False):
        # Clicking the Checkbox
        if first_time:
            await VisualCaptcha.checkbox(page)

        try:
            # Getting the Captcha Frame
            captcha_frame = page.frame_locator("//iframe[contains(@src,'bframe')]")
        except Exception as e:
            # Getting Captcha Token
            captcha_token = await page.evaluate("grecaptcha.getResponse()")
            if captcha_token:
                return captcha_token
            else:
                print("reCaptcha didnt load")
                return False

        for _ in range(10):
            try:
                label_obj = captcha_frame.locator("//strong")
                prompt = await label_obj.text_content()
                VisualCaptcha.label = prompt.strip()
            except:
                captcha_token = await page.evaluate("grecaptcha.getResponse()")
                if captcha_token:
                    return captcha_token
                else:
                    print("reCaptcha didnt load")
                    return False
            break
        else:
            print("Captcha Type of ObjectDetection isnt supported yet")
            return False

        samples = await VisualCaptcha.solve_captcha(page, captcha_frame)

        VisualCaptcha.latest_captcha = await VisualCaptcha.get_first_image(samples.first)

        # Submit challenge
        submit_button = captcha_frame.locator("//button[@id='recaptcha-verify-button']")
        await submit_button.click()

        await page.wait_for_timeout(1000)
        captcha_token = await page.evaluate("grecaptcha.getResponse()")
        if captcha_token:
            return str(captcha_token)
        else:
            # Check if Task was solved incorrectly
            if await VisualCaptcha.get_first_image(samples.first) == VisualCaptcha.latest_captcha:
                # Clicking Reload Button
                reload_button = captcha_frame.locator("#recaptcha-reload-button")
                await reload_button.click()

            return await VisualCaptcha.visual_recaptcha(page, first_time=False)
