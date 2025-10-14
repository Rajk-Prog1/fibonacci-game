import streamlit as st
import subprocess, time, json, os

st.set_page_config(page_title="Fibonacci Game", layout="wide")

FIB_DIR = "fib_files"  # <── folder where all fib files live

# --- Language setup ---
LANGUAGES = {
    "Python": {
        "cmd": ["python", "-u",  f"{FIB_DIR}/fib.py"]
    },
    "C++": {
        "prepare": [["g++", f"{FIB_DIR}/fib.cpp", "-o", f"{FIB_DIR}/fib_bin"]],
        "cmd": [f"./{FIB_DIR}/fib_bin"],
        "cleanup": [["rm", f"{FIB_DIR}/fib_bin"]]
    },
    "Java": {
        "prepare": [["javac", "fib.java"]],
        "cmd": ["java", "-cp", ".", "fib"],
        "cleanup": [["rm", "fib.class"]],
        "cwd": FIB_DIR
    },
    "PHP": {
        "cmd": ["php", os.path.join(FIB_DIR, "fib.php")]
    }
}

# --- Helper function to run each language ---
def run_language(name, cfg):
    """Compile (if needed), run, and capture output/time for one language"""
    st.subheader(f"▶️ Running {name}")
    output_box = st.empty()

    n_val = int(st.session_state.get("n_value", 40))  # <-- user's n value

    # Compile if necessary
    if "prepare" in cfg:
        for prep in cfg["prepare"]:
            subprocess.call(prep, cwd=cfg.get("cwd", None))

    # Run and stream output
    start = time.time()
    process = subprocess.Popen(
        cfg["cmd"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=cfg.get("cwd", None),
        env={**os.environ, "FIB_N": str(n_val)}  # pass n via environment
    )
    lines = []
    for line in process.stdout:
        lines.append(line.strip())
        output_box.text("\n".join(lines[-20:]))  # show last 20 lines
    process.wait()
    elapsed = time.time() - start

    # Cleanup
    if "cleanup" in cfg:
        for clean in cfg["cleanup"]:
            subprocess.call(clean, cwd=cfg.get("cwd", None))

    # Determine expected JSON filename
    result_file = os.path.join(cfg.get("cwd", ""), f"result_{name.lower().replace('+','p')}.json")

    # Read existing JSON (created by the fib script) or create a fallback
    if os.path.exists(result_file):
        with open(result_file, encoding="utf-8") as f:
            result = json.load(f)
    else:
        result = {
            "language": name,
            "n": n_val,
            "sequence": [],
            "seconds": elapsed
        }

    result["seconds"] = round(elapsed, 3)
    return result



# --- Streamlit UI ---
st.title("Multi-Language Fibonacci Game")

# --- Streamlit UI ---
st.title("Multi-Language Fibonacci Game")

# User chooses how many Fibonacci numbers to calculate
n = st.number_input(
    "Enter n (how many Fibonacci numbers to calculate):",
    min_value=1,
    max_value=100,
    value=40,
    step=1
)
st.session_state["n_value"] = n
st.write(f"Each language will calculate the first {n} Fibonacci numbers.")

st.divider()
st.subheader("Run a specific language")

for lang, cfg in LANGUAGES.items():
    if st.button(f"▶️ Run {lang}"):
        st.info(f"Running {lang} — please wait...")
        res = run_language(lang, cfg)
        st.success(f"{lang} finished in {res['seconds']} seconds!")


