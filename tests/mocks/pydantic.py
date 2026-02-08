class BaseModel:
    def __init__(self, **kwargs):
        # Basic validation simulation
        if "age_months" in kwargs and kwargs["age_months"] < 0:
            raise ValidationError("age_months must be >= 0")
        for k, v in kwargs.items():
            setattr(self, k, v)

def Field(*args, **kwargs):
    return kwargs.get('default', None)

class ValidationError(Exception):
    pass
