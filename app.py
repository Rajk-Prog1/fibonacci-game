import streamlit as st
import subprocess, time, json, os

st.set_page_config(page_title="Fibonacci Game", layout="wide")

FIB_DIR = "fib_files"  # <── folder where all fib files live

# --- Language setup ---
LANGUAGES = {
    "Python": {
        "cmd": ["python", f"{FIB_DIR}/fib.py"]
    },
    "C++": {
        "prepare": [["g++", f"{FIB_DIR}/fib.cpp", "-o", f"{FIB_DIR}/fib_bin"]],
        "cmd": [f"./{FIB_DIR}/fib_bin"],
        "cleanup": [["rm", f"{FIB_DIR}/fib_bin"]]
    },
    "Java": {
        "prepare": [["javac", f"{FIB_DIR}/fib.java"]],
        "cmd": ["java", "-cp", f"./FIB_DIR/", "fib"],
        "cleanup": [["rm", f"{FIB_DIR}/fib.class"]]
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

    # Compile if necessary
    if "prepare" in cfg:
        for prep in cfg["prepare"]:
            subprocess.call(prep)

    # Run and stream output
    start = time.time()
    process = subprocess.Popen(cfg["cmd"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines = []
    for line in process.stdout:
        lines.append(line.strip())
        output_box.text("\n".join(lines[-20:]))  # show last 20 lines
    process.wait()
    elapsed = time.time() - start

    # Cleanup
    if "cleanup" in cfg:
        for clean in cfg["cleanup"]:
            subprocess.call(clean)

    # Determine expected JSON filename
    result_file = f"{FIB_DIR}/result_{name.lower().replace('+','p')}.json"

    # Read existing JSON (created by the fib script) or create a fallback
    if os.path.exists(result_file):
        with open(result_file, encoding="utf-8") as f:
            result = json.load(f)
    else:
        result = {
            "language": name,
            "n": 40,
            "sequence": [],
            "seconds": elapsed
        }

    result["seconds"] = round(elapsed, 3)
    return result


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

if st.button("Run All Benchmarks"):
    st.info("Running all language benchmarks — may take up to a minute...")
    results = []

    for lang, cfg in LANGUAGES.items():
        res = run_language(lang, cfg)
        results.append(res)
        st.success(f"{lang} finished in {res['seconds']} seconds")

    # Save all results
    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    st.balloons()
    st.info("All benchmarks complete! Results saved to results.json")

# --- Results viewer ---
st.divider()
st.header("Previous Results")

if os.path.exists("results.json"):
    with open("results.json", encoding="utf-8") as f:
        results = json.load(f)

    for r in results:
        st.subheader(f"{r['language']} — {r['seconds']} seconds")
        with st.expander(f"Show Fibonacci sequence for {r['language']}"):
            seq = r.get("sequence", [])
            if seq:
                st.text(", ".join(map(str, seq)))
            else:
                st.warning("No sequence found in result file.")
else:
    st.warning("No previous results yet — click 'Run All Benchmarks' to start.")

