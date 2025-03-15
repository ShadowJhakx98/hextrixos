import torch
import torch.nn as nn
import torchvision.models as models

class NeuralStyleTransfer:
    def __init__(self):
        self.vgg = models.vgg19(pretrained=True).features.eval()
        self.style_layers = ['0', '5', '10', '19', '28']
        self.content_layers = ['21']
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
    def extract_features(self, x):
        features = []
        for name, layer in self.vgg._modules.items():
            x = layer(x)
            if name in self.style_layers + self.content_layers:
                features.append(x)
            if name == self.content_layers[0]:
                break
        return features

    def calculate_loss(self, content, style, generated):
        content_loss = torch.mean((generated - content)**2)
        style_loss = 0
        for gen_feat, style_feat in zip(generated, style):
            _, d, h, w = gen_feat.size()
            G = torch.mm(gen_feat.view(d, h*w), gen_feat.view(d, h*w).t())
            A = torch.mm(style_feat.view(d, h*w), style_feat.view(d, h*w).t())
            style_loss += torch.mean((G - A)**2)
        return content_loss + style_loss * 1e6

class DistributedStyleTrainer:
    def __init__(self, num_gpus=4):
        self.num_gpus = num_gpus
        self.model = NeuralStyleTransfer()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        
    def train_batch(self, content_batch, style_batch):
        # Distributed training logic
        if torch.cuda.device_count() > 1:
            self.model = nn.DataParallel(self.model)
        self.model.to(self.device)
        
        content_features = self.model.extract_features(content_batch)
        style_features = self.model.extract_features(style_batch)
        
        self.optimizer.zero_grad()
        loss = self.calculate_loss(content_features, style_features)
        loss.backward()
        self.optimizer.step()
        return loss.item()
