import numpy as np
import pandas as pd
from torchvision.models import vgg16, VGG16_Weights
import torch
import xgboost as xgb
import emoji

class LikeScorer():
    def __init__(self, dtype):
        super().__init__()
        self.model_like = xgb.Booster()
        self.model_like.load_model("C:\DS_Lab_Project\RL_Model\ddpo_pytorch\model_like.json")
        self.model_VGG = vgg16(pretrained=True)
        self.weights = VGG16_Weights.DEFAULT
        self.model_VGG.eval().cuda()
        self.dtype = dtype

    @torch.no_grad()
    def __call__(self, images):
        preprocess = self.weights.transforms()
        results = []
        for img in images:
            batch = preprocess(img).unsqueeze(0)
            prediction = self.model_VGG(batch).squeeze(0).softmax(0)
            img_info = xgb.DMatrix(np.array(prediction.tolist()).reshape((1,-1)))
            result_like = int(self.model_like.predict(img_info))
            results.append(result_like)
        
        return results
