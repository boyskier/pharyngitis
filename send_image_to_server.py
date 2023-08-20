import requests
import base64
from PIL import Image
import io

url = "http://localhost:5000/upload"
data = {
    'user_name': 'patient2'
}

img_path = 'sample_images/2.JPG'
files = {
    'file': open(img_path, 'rb')
}

response = requests.post(url, files=files, data=data)

if response.status_code == 200:
    response_data = response.json()
    probability = response_data['probability']
    print(f"Probability: {probability}")

    image_base64 = response_data['image']
    image_data = base64.b64decode(image_base64)
    image = Image.open(io.BytesIO(image_data))
    image.show()
else:
    print(f"Error: {response.text}")
