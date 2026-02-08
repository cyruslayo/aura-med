import torch
import torch.nn as nn
from src.config import PROJECTION_INPUT_DIM

class ProjectionLayer(nn.Module):
    """
    Bridges the gap between HeAR audio embeddings (1024) 
    and MedGemma LLM embedding space.
    """
    def __init__(self, input_dim: int = PROJECTION_INPUT_DIM, output_dim: int = 2560):
        super().__init__()
        self.projection = nn.Sequential(
            nn.Linear(input_dim, output_dim),
            nn.LayerNorm(output_dim),
            nn.GELU(),
            nn.Linear(output_dim, output_dim)
        )
        print(f"Initialized ProjectionLayer: {input_dim} -> {output_dim}")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.projection(x)
