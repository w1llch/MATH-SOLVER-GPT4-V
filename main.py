import json

import openai
from PIL import Image
from PIL import ImageGrab
from pynput import mouse
from pynput.mouse import Listener
from openai import OpenAI
import base64
import requests

# input api key
api_key = ''


# returns the position of mouse on click1 and click2
def returnpoints():
    points = []

    def on_click(x, y, button, pressed):
        if pressed:
            points.append([x, y])
        if not pressed and len(points) == 2:
            return False

    with Listener(on_click=on_click) as listener:
        listener.join()
    return points


positions = returnpoints()


# makes it possible to start the box at any point. without it, you would have to start at top left point and end at
# bottom right
def create_snipping_box(positions):
    if positions[0][1] > positions[1][1]:
        temp = positions[0][1]
        positions[0][1] = positions[1][1]
        positions[1][1] = temp
    if positions[1][0] < positions[0][0]:
        temp = positions[0][0]
        positions[0][0] = positions[1][0]
        positions[1][0] = temp

    return positions


boxposlist = []
positions2 = create_snipping_box(positions)
boxposlist.append(positions2[0][0])
boxposlist.append(positions2[0][1])
boxposlist.append(positions2[1][0])
boxposlist.append(positions2[1][1])
boxposition = tuple(boxposlist)


# takes the screenshot
def snip_image(coordinates):
    image = ImageGrab.grab(bbox=coordinates)
    return image


screenshot = snip_image(boxposition)
screenshot.save('will.jpg')


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


# Path to your image
image_path = "will.jpg"

# Getting the base64 string
base64_image = encode_image(image_path)

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

payload = {
    "model": "gpt-4-vision-preview",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """Please estimate the area under the curve from [0,7] using midpoint riemann sums"""
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ],
    # "max_tokens": 1000
}

response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

print(response.json())
