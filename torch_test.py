import torch

x = torch.rand(1000, 1000).cuda()
y = torch.mm(x, x)
print(
    "✅ Torch работает на GPU:", y.is_cuda, torch.__version__, torch.cuda.is_available()
)
