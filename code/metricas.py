import time, tracemalloc

def metrica(func, args=(), kwargs=None):
    if kwargs is None:
        kwargs = {}
    tracemalloc.start()
    start = time.time()
    res = func(*args, **kwargs)
    end = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"{func.__name__}: {end - start:.4f}s | Memória: {peak / 1024 / 1024:.4f} MB")
    return res
