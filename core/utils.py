import os

def to_python_float(obj):
    if isinstance(obj, (float, int)):
        return obj
    if hasattr(obj, "item"):          # np.float64, np.int64
        return obj.item()
    if isinstance(obj, list):
        return [to_python_float(x) for x in obj]
    if isinstance(obj, dict):
        return {k: to_python_float(v) for k, v in obj.items()}
    return obj

def short_name(path):
    return os.path.basename(path) if path else ""

