import os, json, time

def fib(n):
    if n <= 2:
        return 1
    return fib(n - 1) + fib(n - 2)

if __name__ == "__main__":
    n = int(os.getenv("FIB_N", "40"))

    start = time.time()
    sequence = []
    for i in range(1, n + 1):
        val = fib(i)
        sequence.append(val)
        print(f"{i}. fibonacci: {val}")
    elapsed = time.time() - start

    result = {
        "language": "Python",
        "n": n,
        "sequence": sequence,
        "seconds": elapsed
    }

    with open("result_python.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

