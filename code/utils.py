# code/utils.py
from time import perf_counter_ns
from functools import wraps

def time_operation(func):
    """
    Decorator to measure 'Wall-Clock' time in milliseconds.
    Professional precision for database and algorithm benchmarks.
    """
    @wraps(func)  # Keeps function metadata (like __name__) intact
    def wrapper(*args, **kwargs):
        start = perf_counter_ns()
        result = func(*args, **kwargs)
        end = perf_counter_ns()
        duration_ms = (end - start) / 1_000_000
        return result, duration_ms
    return wrapper
