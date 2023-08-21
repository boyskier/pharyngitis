import requests
import base64
from PIL import Image
import io


def to_server(user_name='patient1', img_path='sample_images/2.JPG', mode='pharyngitis'):  # mode: pharyngitis, otscope
    url = f"http://localhost:5000/upload/{mode}"
    data = {'user_name': user_name}
    files = {'file': open(img_path, 'rb')}

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


to_server(user_name='patient2', img_path='sample_images/10.JPG', mode='pharyngitis')
