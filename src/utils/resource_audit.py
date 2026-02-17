import functools
import psutil
import time
import logging
from typing import Any, Callable
from src.datatypes import EdgeConstraintViolation
from src.config import MAX_RAM_GB, MAX_INFERENCE_TIME_SEC

logger = logging.getLogger(__name__)

BYTES_TO_GB = 1024 ** 3

def audit_resources(func: Callable) -> Callable:
    """
    Decorator to monitor RAM usage and estimate computational cost.
    Ensures the execution stays within edge-native constraints.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        process = psutil.Process()
        
        # Start measurements
        start_mem = process.memory_info().rss / BYTES_TO_GB
        start_time = time.monotonic()
        
        result = None
        try:
            # Execute the function
            result = func(*args, **kwargs)
            return result
        finally:
            # End measurements - runs even if function raised
            end_mem = process.memory_info().rss / BYTES_TO_GB
            end_time = time.monotonic()
            
            latency = end_time - start_time
            peak_mem = max(start_mem, end_mem)
            
            # Simulated FLOPs calculation (Heuristic)
            estimated_flops_g = latency * 0.5
            
            # Resource Policy Enforcement
            if peak_mem > MAX_RAM_GB:
                raise EdgeConstraintViolation(
                    f"Edge Constraint Violation: Peak RAM {peak_mem:.2f} GB "
                    f"exceeds limit of {MAX_RAM_GB} GB."
                )
            
            # Logging requirements (M1: Use logger instead of print)
            logger.info("Simulated RAM: %.2f GB", peak_mem)
            logger.info("Estimated FLOPs: %.2f G", estimated_flops_g)
            
            # If the result is a TriageResult, populate it (M3: Standardize keys)
            if result is not None and hasattr(result, 'usage_stats'):
                if result.usage_stats is None:
                    result.usage_stats = {}
                
                result.usage_stats.update({
                    "ram_gb": round(peak_mem, 2),
                    "flops_g": round(estimated_flops_g, 2),
                    "latency_sec": round(latency, 3),
                    "max_allowed_sec": MAX_INFERENCE_TIME_SEC
                })
    return wrapper
