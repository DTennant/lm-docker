import torch
import torch.nn as nn

# 确保有 GPU
assert torch.cuda.is_available()

# 初始化一个简单的 GPU 占用模型
model = nn.Sequential(
            torch.hub.load('pytorch/vision:v0.6.0', 'resnet101', pretrained=False, verbose=False)
        ).cuda()

# 一个长时间运行的循环，以保持 GPU 占用
while True:
    input_tensor = torch.randn(64, 3, 224, 224).cuda()
    output = model(input_tensor)
