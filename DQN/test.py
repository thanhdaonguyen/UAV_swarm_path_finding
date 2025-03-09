import torch

a = torch.tensor([[1, 99], [3, 4]])
print((a==torch.max(a)).nonzero())