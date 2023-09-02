#1
import torch
from PIL import Image

#2
from Fever_pytorch_structure import IdentityLayer, CustomModel, HuggingfaceCustomModel

#3 - 이미지, 모델 load
image = Image.open("./data/0_Normal_val/normal_2.tiff")
model = torch.load("./models/alexnet_model.pth")

#4 - 모델 device 이동
#model.to('cpu')
model.to(torch.device("cuda"))

#5 - 이미지 전처리 및 텐서화
tensor = model.transformer(image)

#6 - 이미지 텐서 shape 조정 (batch_size 자리 1로 맞추기)
tensor = tensor.unsqueeze(dim=0)

#7 - 평가모드 전환 후 결과 얻기
model.eval()
output = model(tensor)[0]

#8 - 확률로 변환
probability = float(model.prob_func(output))

#9 - 출력(optional)
print(probability)
