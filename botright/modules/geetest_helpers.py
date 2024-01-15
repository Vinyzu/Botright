# from __future__ import annotations
#
# import base64
# import io
# import logging
# import os
# import random
# from typing import Optional, List, Any, Tuple, Literal, Union
#
# import cv2
# import easyocr
# import yolov5
# import numpy as np
# from numpy.typing import NDArray
# from numpy import uint8
#
# from PIL import Image
# from scipy import ndimage
# from sentence_transformers import SentenceTransformer, util
# from skimage.metrics import structural_similarity
#
# logging.getLogger("yolov5").disabled = True
# logging.getLogger(__name__).disabled = True  # SentenceTransformer
#
#
# def solve_icon_captcha(_captcha: Union[bytes, NDArray[uint8]], _template: Union[bytes, NDArray[uint8]], mode: Optional[str] = "canny") -> List[List[int]]:
#     if isinstance(_captcha, bytes):
#         captcha_nparr = np.frombuffer(_captcha, np.uint8)
#         captcha = cv2.imdecode(captcha_nparr, cv2.IMREAD_COLOR)
#     else:
#         captcha = _captcha
#
#     if isinstance(_template, bytes):
#         template_nparr = np.frombuffer(_template, np.uint8)
#         template = cv2.imdecode(template_nparr, cv2.IMREAD_COLOR)
#     else:
#         template = _template
#
#     dir_path = os.path.dirname(os.path.realpath(__file__))
#     # init yolov5 model
#     model = yolov5.load(f"{dir_path}\\geetest.torchscript", device="cpu", verbose=False, autoshape=True)
#     results = model(captcha)
#
#     # show detection bounding boxes on image
#     pd = results.pandas().xyxy[0]
#     # Converting to Dict
#     results_dict = pd.to_dict(orient="index")
#
#     # Cropping and Monochroming the Results
#     target_images = []
#     # For retrieving the Captcha Coords later
#     target_img_coords = {}
#     for result in results_dict.values():
#         x1, y1, x2, y2 = (int(result["xmin"]), int(result["ymin"]), int(result["xmax"]), int(result["ymax"]))
#         # Calculating the Middle of the CaptchaIcon
#         widht, height = x2 - x1, y2 - y1
#         midx, midy = x1 + int(widht // 2), y1 + int(height // 2)
#
#         cropped_im = captcha[y1:y2, x1:x2]
#
#         target_images.append(cropped_im)
#
#         retval, buffer = cv2.imencode(".jpg", cropped_im)
#         jpg_as_text = base64.b64encode(buffer)  # type: ignore
#
#         target_img_coords[jpg_as_text] = [midx, midy]
#
#     if mode == "random":
#         coords = list(target_img_coords.values())
#         random.shuffle(coords)
#         return coords
#
#     def is_row_all_white(img, x):
#         height, width, *_ = img.shape
#         colors = []
#         for y in range(height):
#             color = template[y, x]
#             colors.append(color)
#         # colors = [img[x, y] for y in range(height)]
#         for color in colors:
#             if isinstance(color, np.uint):
#                 if not color > 220:
#                     return False
#             else:
#                 r, g, b = color
#                 if not (r > 220 and g > 220 and b > 220):
#                     return False
#         return True
#
#     def resize_image_to_fit(img):
#         minus = 0
#         height, width, *_ = img.shape
#         for x in range(width):
#             white = is_row_all_white(img, x)
#             # If a whole column of the Image is white
#             if white:
#                 cut = x - minus
#                 # Delete the Column from the Image
#                 img = np.delete(img, cut, 1)
#                 minus += 1
#         # Returning cut Image
#         return img
#
#     target_pane = resize_image_to_fit(template)
#
#     blocks = len(target_images)
#     templates = []
#     for i in range(blocks):
#         height, width, *_ = target_pane.shape
#         block_size = width // blocks
#         start, end = block_size * i, block_size * int(i + 1)
#
#         templates.append(target_pane[0:height, start:end])
#
#     if mode == "ssim":
#         similarities = []
#         for target in target_images:
#             similarity = []
#             for i, template in enumerate(templates):
#                 best = 0
#                 # The Captcha Images can be rotated anywhere from -36° to 36° (*2 Because 2 Images are both rotated)
#                 for degree in range(-72, 72, 6):
#                     rotated = ndimage.rotate(template, degree, reshape=False)
#                     # Resizing the Image to be the same size
#                     height, widht = target.shape[:2]
#                     resized = cv2.resize(target, (widht, height), interpolation=cv2.INTER_AREA)
#                     # Greyscaling Images
#                     target_grey, template_grey = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY), cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
#                     # Predicting the Similarity with ssim
#                     ssim_score = structural_similarity(target_grey, template_grey)
#                     # If the ssim is the Best
#                     if ssim_score > best:
#                         best = ssim_score
#                 similarity.append(best)
#             similarities.append(similarity)
#
#     elif mode == "clip":
#         # Loading the ClipModel
#         model = SentenceTransformer("clip-ViT-B-32", device="cpu")
#
#         similarities = []
#         for target in target_images:
#             similarity = [0 for _ in range(len(templates))]
#             im_pil0 = Image.fromarray(target)
#
#             # The Captcha Images can be rotated anywhere from -36° to 36° (*2 Because 2 Images are both rotated)
#             for degree in range(-72, 72, 6):
#                 # Rotating all Templates by a specific degree
#                 rotated = [ndimage.rotate(template, degree, reshape=False) for template in templates]
#                 # Converting these Images to Pillow
#                 templates_pil = [Image.fromarray(template) for template in rotated] + [im_pil0]
#                 # Predicting the Similarity of those Rotated Pillow Images with the Target
#                 encoded_image = model.encode([im_pil0] + templates_pil, batch_size=128, convert_to_tensor=True, show_progress_bar=False)  # type: ignore
#                 # Processing the Prediction
#                 processed_images = util.paraphrase_mining_embeddings(encoded_image)
#                 # Deleting all the Prediction which doesnt have the Target in them (Model also predicts Template against Template)
#                 only_with_template = {}
#                 for result in processed_images:
#                     score, node0, node1 = result
#                     if node0 == 0:
#                         only_with_template[node1] = score
#                     elif node1 == 0:
#                         only_with_template[node0] = score
#                 # Sorting the Predictions
#                 sort = dict(sorted(only_with_template.items()))
#                 for i, val in enumerate(list(sort.values())):
#                     if val > similarity[i]:
#                         similarity[i] = val
#             similarities.append(similarity)
#
#     else:
#         similarities = []
#         for target in target_images:
#             similarity = []
#             for i, template in enumerate(templates):
#                 best = 0
#                 # Resizing the Image to be the same size
#                 height, widht = target.shape[:2]
#                 resized = cv2.resize(template, (widht, height), interpolation=cv2.INTER_AREA)
#                 # The Captcha Images can be rotated anywhere from -36° to 36° (*2 Because 2 Images are both rotated)
#                 for degree in range(-72, 72, 6):
#                     rotated = ndimage.rotate(resized, degree, reshape=True)
#                     # Blurring Template for cleaner Contours
#                     # blurred_template = cv2.GaussianBlur(rotated, (9, 9), 0)
#                     # converting image into grayscale image
#                     # gray_template = cv2.cvtColor(blurred_template, cv2.COLOR_BGR2GRAY)
#                     # Detecing Contours with Canny
#                     template_canny = cv2.Canny(rotated, 50, 400)
#
#                     # Detecing Contours with Canny
#                     canny = cv2.Canny(target, 50, 250)
#
#                     # Performing Template Matching of the Contours
#                     result = cv2.matchTemplate(canny, template_canny, cv2.TM_CCOEFF_NORMED)
#                     minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(result)
#                     if maxVal > best:
#                         best = int(maxVal)
#                 similarity.append(best)
#             similarities.append(similarity)
#
#     mapping = {}
#     for i in range(len(similarities)):
#         bests = {}
#         for j in range(len(similarities)):
#             bests[j] = max(similarities[j])
#
#         best_index = max(bests, key=lambda index: bests[index])
#         best = bests[best_index]
#         best_subindex = similarities[best_index].index(best)
#
#         similarities[best_index] = [0, 0, 0, 0]
#         for sim in similarities:
#             try:
#                 sim[best_subindex] = 0
#             except Exception:
#                 pass
#
#         mapping[best_index] = best_subindex
#
#     sorted_map = dict(sorted(mapping.items()))
#     final = []
#     for key, val in sorted_map.items():
#         img = target_images[val]
#
#         retval, buffer = cv2.imencode(".jpg", img)
#         jpg_as_text = base64.b64encode(buffer)  # type: ignore
#         final.append(target_img_coords[jpg_as_text])
#
#     return final
#
#
# def solve_nine_captcha(_captcha: bytes, template: bytes) -> List[List[int]]:
#     # Using OCR to Read the Captcha Prompt
#     reader = easyocr.Reader(["en"])
#     result = reader.readtext(template, detail=0)
#     captcha_prompt = result[0]
#     # Load CLIP model
#     model = SentenceTransformer("clip-ViT-B-32")
#
#     # Tiling the Image into pieces
#     def tile(im, xPieces, yPieces):
#         tiles = []
#         imgwidth, imgheight = im.size
#         height = imgheight // yPieces
#         width = imgwidth // xPieces
#         for i in range(0, yPieces):
#             for j in range(0, xPieces):
#                 box = (j * width, i * height, (j + 1) * width, (i + 1) * height)
#                 a = im.crop(box)
#                 tiles.append(a)
#         return tiles, height, width
#
#     # Loading the Image with Pillow
#     captcha = Image.open(io.BytesIO(_captcha))
#     # Encode an image:
#     tiles, tile_height, tile_width = tile(captcha, 3, 3)
#     img_emb = model.encode(tiles)
#     # Encode text descriptions
#     text_emb = model.encode(captcha_prompt)
#     # Compute cosine similarities
#     cos_scores = util.cos_sim(text_emb, img_emb)
#     result = cos_scores[0].tolist()
#
#     def get_best_matches(result):
#         best = {}
#         bests = sorted(result)[-4:]
#         average = sum(bests) / len(bests)
#         for item in result:
#             if item > average:
#                 best[result.index(item)] = item
#         return best
#
#     # Predicting which Images are True
#     best_matches = get_best_matches(result)
#
#     # Calculating the Coordinates of the Matches
#     best_coords = []
#     for index in best_matches:
#         x = index % 3
#         y = index // 3
#         x_coord, y_coord = (x * tile_width + tile_width // 2, y * tile_height + tile_height // 2)
#         best_coords.append([x_coord, y_coord])
#
#     return best_coords
#
#
# def solve_slider_captcha(_captcha: bytes, _template: bytes) -> int:
#     # reading image
#     template = cv2.imdecode(np.frombuffer(_template, np.uint8), -1)
#     # Blurring Template for cleaner Contours
#     blurred_template = cv2.GaussianBlur(template, (9, 9), 0)
#     # converting image into grayscale image
#     gray_template = cv2.cvtColor(blurred_template, cv2.COLOR_BGR2GRAY)
#     # Detecing Contours with Canny
#     template_canny = cv2.Canny(gray_template, 50, 400)
#
#     # reading image
#     img = cv2.imdecode(np.frombuffer(_captcha, np.uint8), -1)
#     # Blurring Template for cleaner Contours
#     blurred = cv2.GaussianBlur(img, (3, 3), 0)
#     # Detecing Contours with Canny
#     canny = cv2.Canny(blurred, 50, 250)
#
#     # Performing Template Matching of the Contours
#     result = cv2.matchTemplate(canny, template_canny, cv2.TM_CCOEFF_NORMED)
#     minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(result)
#     # Getting the Coordinates of the most matching Location
#
#     startX: int = maxLoc[0]
#
#     # endX = startX + template.shape[1]
#     # endY = startY + template.shape[0]
#     # # draw the bounding box on the image
#     # cv2.rectangle(img, (startX, startY), (endX, endY), (255, 0, 0), 3)
#     # # show the output image
#     # cv2.imshow("Output", img)
#     # cv2.waitKey(0)
#     # cv2.destroyAllWindows()
#
#     return startX
#
#
# def solve_icon_crush(grid: List[List[Optional[str]]]) -> Tuple[List[int], List[int]]:
#     # Helpers
#     def most_common(lst: List[Any]) -> Any:
#         not_none: List[Any] = list(filter(None, lst))
#         if not any(not_none):
#             return None
#         return max(set(not_none), key=not_none.count)
#
#     columns = list(zip(*grid))
#
#     # Rows
#     for row in grid:
#         good = most_common(row)
#         count = row.count(good)
#         if count == len(row) - 1:
#             bools = [x == good for x in row]
#             not_index = bools.index(False)
#             wanted_index = [grid.index(row), not_index]
#             row_index, item_index = wanted_index
#
#             column = columns[item_index]
#             neighbours = [next(iter(column[row_index - 1: row_index]), None), next(iter(column[row_index + 1: row_index + 2]), None)]
#             for neighbor in neighbours:
#                 if neighbor == good:
#                     addition = -1 if not neighbours.index(neighbor) else 1
#                     good_index = [row_index + addition, columns.index(column)]
#                     return good_index, wanted_index
#
#     for column in columns:
#         good = most_common(list(column))
#         count = column.count(good)
#         if count == len(column) - 1:
#             bools = [x == good for x in column]
#             not_index = bools.index(False)
#             wanted_index = [not_index, columns.index(column)]
#             row_index, item_index = wanted_index
#
#             row = grid[row_index]
#             neighbours = [next(iter(row[item_index - 1: item_index]), None), next(iter(row[item_index + 1: item_index + 2]), None)]
#
#             for neighbor in neighbours:
#                 if neighbor == good:
#                     addition = -1 if not neighbours.index(neighbor) else 1
#                     good_index = [grid.index(row), item_index + addition]
#                     return good_index, wanted_index
#
#     return [0, 0], [1, 1]
#
#
# def solve_grid_captcha(grid: List[List[Union[str, int, None]]], switch_elements: Optional[bool] = False) -> Union[Tuple[List[int], List[int]], Literal[False]]:
#     # Helpers
#     def most_common(lst: List[Any]):
#         not_none: List[Any] = list(filter(None, lst))
#         if not any(not_none):
#             return None
#         return max(set(not_none), key=not_none.count)
#
#     def find_point(haystack: List[Any], needle: Any):
#         return next(elem for elem in haystack if needle in elem)
#
#     # Rows
#     for row in grid:
#         good = most_common(row)
#         count = row.count(good)
#         others = [value for value in row if value != good]
#         switch0, switch1 = (count == len(row) - 1), (count == len(row) - 1 and not any(others))
#         if switch0 if switch_elements else switch1:
#             bools = [x == good for x in row]
#             not_index = bools.index(False)
#             wanted_index = [grid.index(row), not_index]
#
#             rows_without_row = [n for n in grid if n != row]
#             good_row = find_point(rows_without_row, good)
#             good_index = [grid.index(good_row), good_row.index(good)]
#             return good_index, wanted_index
#
#     # Columns
#     columns = list(zip(*grid))
#     for column in columns:
#         good = most_common(list(column))
#         count = column.count(good)
#         others = [value for value in column if value != good]
#         switch0, switch1 = (count == len(column) - 1), (count == len(column) - 1 and not any(others))
#         if switch0 if switch_elements else switch1:
#             bools = [x == good for x in column]
#             not_index = bools.index(False)
#             wanted_index = [not_index, columns.index(column)]
#
#             columns_without_column = [n for n in columns if n != column]
#             good_column = find_point(columns_without_column, good)
#             good_index = [good_column.index(good), columns.index(good_column)]
#             return good_index, wanted_index
#
#     # Diagonals
#     down_diagonal = [grid[i][i] for i in range(len(grid))]
#     good = most_common(down_diagonal)
#     count = down_diagonal.count(good)
#     others = [value for value in down_diagonal if value != good]
#     switch0, switch1 = (count == len(down_diagonal) - 1), (count == len(down_diagonal) - 1 and not any(others))
#     if switch0 if switch_elements else switch1:
#         bools = [x == good for x in down_diagonal]
#         not_index = bools.index(False)
#         wanted_index = [not_index, not_index]
#
#         # Turning Values into 0s for searching
#         grid_without_diagonal = list(grid)
#         for i in range(len(grid)):
#             grid_without_diagonal[i][i] = 0
#         good_row = find_point(grid_without_diagonal, good)
#         good_index = [grid.index(good_row), good_row.index(good)]
#
#         return good_index, wanted_index
#
#     up_diagonal = [grid[i][len(grid) - 1 - i] for i in range(len(grid))]
#     good = most_common(up_diagonal)
#     count = up_diagonal.count(good)
#     others = [value for value in up_diagonal if value != good]
#     switch0, switch1 = (count == len(up_diagonal) - 1), (count == len(up_diagonal) - 1 and not any(others))
#     if switch0 if switch_elements else switch1:
#         bools = [x == good for x in up_diagonal]
#         not_index = bools.index(False)
#         wanted_index = [not_index, len(grid) - 1 - not_index]
#
#         # Turning Values into 0s for searching
#         grid_without_diagonal = list(grid)
#         for i in range(len(grid)):
#             grid_without_diagonal[i][len(grid) - 1 - i] = 0
#         good_row = find_point(grid_without_diagonal, good)
#         good_index = [grid.index(good_row), good_row.index(good)]
#
#         return good_index, wanted_index
#
#     return False
