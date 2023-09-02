#1
import torch.nn as nn
from torchvision import transforms

#2
class IdentityLayer(nn.Module):
    def __init__(self):
        super(IdentityLayer, self).__init__()

    def forward(self, x):
        return x

#3
# origin_model과 new_model을 합쳐서 출력하는 CustomModel 클라스
global CustomModel
class CustomModel(nn.Module):

    def __init__(self, origin_model, new_model):
        super().__init__()

        # 기본 변수 선언
        self.origin_model = origin_model
        self.new_model = new_model
        self.device = 'cpu'

        # 사용하는 transformer, prob_func (torch.save 저장용)
        self.transformer = None
        self.prob_func = None

    # nn.Module 기본 to 함수 오버라이딩
    def to(self, device):
        self.device = device
        return super().to(device)

    # 일반 모델에서 inputs를 받아 origin model에 넣은 후 outputs를 반환
    # inputs.shape = torch.Size([batch_size, 3(RGB값), 세로, 가로])
    def origin_output(self, inputs):

        # self.device로 inputs 이동
        if self.device != 'cpu':
            inputs = inputs.to(self.device)

        # outputs
        outputs = self.origin_model(inputs)
        return outputs

    def forward(self, inputs):

        # origin output 받아서 new_model에 넣어 결과 return
        origin_outputs = self.origin_output(inputs)
        new_outputs = self.new_model(origin_outputs)
        return new_outputs

#4
# origin_model과 new_model을 합쳐서 출력하는 CustomModel 클라스
global HuggingfaceCustomModel
class HuggingfaceCustomModel(CustomModel):

    # huggingface 모델에서 inputs를 받아 output을 반환하는 함수
    # inputs.shape = torch.Size([batch_size, 3(RGB값), 세로, 가로])
    def origin_output(self, inputs):

        # tensor를 image로 바꾸어 image_list 생성
        image_list = []
        for a_tensor in inputs:
            a_tensor = a_tensor.to(self.device)
            a_image = transforms.ToPILImage()(a_tensor)
            image_list.append(a_image)

        # processing
        processed_inputs = self.processor(images=image_list, return_tensors="pt")

        # self.device로 processed_inputs 이동
        if self.device != 'cpu':
            processed_inputs = processed_inputs.to(self.device)

        # outputs
        outputs = self.origin_model(**processed_inputs)

        # outputs dictionary에서 output_key_name을 찾아 outputs 반환
        outputs = outputs[self.output_key_name]

        return outputs
