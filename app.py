import streamlit as st
import subprocess, time, json, os
import pandas as pd
import math
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# Load credentials from Streamlit secrets
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=SCOPES
)
client = gspread.authorize(creds)

SHEET_ID = st.secrets["sheet_info"]["SHEET_ID"]
SHEET_NAME = st.secrets["sheet_info"]["SHEET_NAME"]

sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
df = pd.DataFrame(sheet.get_all_records())


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
    """Compile (if needed), run, capture output/time, save results, and update leaderboard."""
    st.subheader(f"▶️ Running {name}")
    output_box = st.empty()

    n_val = int(st.session_state.get("n_value", 40))  # user's selected n

    # --- Compile if needed ---
    if "prepare" in cfg:
        for prep in cfg["prepare"]:
            subprocess.call(prep, cwd=cfg.get("cwd", None))

    # --- Run and stream output ---
    start = time.time()
    process = subprocess.Popen(
        cfg["cmd"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=cfg.get("cwd", None),
        env={**os.environ, "FIB_N": str(n_val)}
    )
    lines = []
    for line in process.stdout:
        lines.append(line.strip())
        output_box.text("\n".join(lines[-20:]))  # show rolling output
    process.wait()
    elapsed = time.time() - start

    # --- Cleanup ---
    if "cleanup" in cfg:
        for clean in cfg["cleanup"]:
            subprocess.call(clean, cwd=cfg.get("cwd", None))

    # --- Prepare result file path ---
    result_file = os.path.join(cfg.get("cwd", ""), f"result_{name.lower().replace('+','p')}.json")

    # --- Load or create result ---
    if os.path.exists(result_file):
        with open(result_file, encoding="utf-8") as f:
            result = json.load(f)
    else:
        result = {"language": name, "n": n_val, "sequence": [], "seconds": elapsed}

    # --- Update time and save ---
    result["seconds"] = round(elapsed, 3)

    # Load previous results.json
    if os.path.exists("results.json"):
        with open("results.json", "r", encoding="utf-8") as f:
            all_results = json.load(f)
    else:
        all_results = []

    # Update or add current language
    updated = False
    for r in all_results:
        if r["language"] == name:
            r.update(result)
            updated = True
            break
    if not updated:
        all_results.append(result)

    # Save updated results.json
    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    st.success(f"{name} finished in {result['seconds']} seconds!")

    # --- Reload leaderboard dynamically ---
    try:
        df = load_guesses()
        with open("results.json", "r", encoding="utf-8") as f:
            actual_data = json.load(f)
        actual = {row["language"]: row["seconds"] for row in actual_data}

        leaderboard = compute_leaderboard(df, actual)
        if not leaderboard.empty:
            st.subheader("🏆 Updated Leaderboard")
            st.dataframe(leaderboard, use_container_width=True)
        else:
            st.info("No guesses or results available yet.")
    except Exception as e:
        st.error(f"Error updating leaderboard: {e}")

    return result


# --- Forgiving logarithmic scoring function ---
def forgiving_score(guess, actual, k=1.0, round_digits = 4):
    """Calculate a forgiving logarithmic accuracy score (0–100%)."""
    try:
        guess = float(guess)
        if guess <= 0 or actual <= 0:
            return 0
        error = abs(math.log10(guess / actual))
        return round(100 * math.exp(-k * error), round_digits)
    except Exception:
        return 0


# --- Helper: Load guesses from Google Sheet ---
def load_guesses():
    """Read form responses into a DataFrame."""
    try:
        sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
        df = pd.DataFrame(sheet.get_all_records())
        # Rename columns (your Hungarian Google Form headers)
        df.rename(columns={
            "Név": "Name",
            "Python (másodpercben)": "Python",
            "C++ (másodpercben)": "C++",
            "Java (másodpercben)": "Java",
            "PHP (másodpercben)": "PHP",
        }, inplace=True)
        return df
    except Exception as e:
        st.error(f"Error loading Google Sheet: {e}")
        return pd.DataFrame()


# --- Helper: Compute leaderboard ---
def compute_leaderboard(df, actual):
    """Compute scores and return a sorted leaderboard DataFrame."""
    if df.empty or not actual:
        return pd.DataFrame()

    for lang in ["Python", "C++", "Java", "PHP"]:
        df[f"{lang}_score"] = df[lang].apply(lambda g: forgiving_score(g, actual.get(lang, 0)))

    df["Final_score"] = df[[f"{lang}_score" for lang in ["Python", "C++", "Java", "PHP"]]].mean(axis=1)
    df.sort_values("Final_score", ascending=False, inplace=True)

    ordered_cols = [
        "Name",
        "Python", "Python_score",
        "C++", "C++_score",
        "Java", "Java_score",
        "PHP", "PHP_score",
        "Final_score"
    ]
    return df[ordered_cols]

# --- Streamlit UI ---
st.title("Multi-Language Fibonacci Game")

# --- Leaderboard section ---
st.title("🏆 Fibonacci Speed Challenge — Leaderboard")

# Load actual benchmark results (if available)
try:
    with open("results.json", "r", encoding="utf-8") as f:
        actual_data = json.load(f)
    actual = {row["language"]: row["seconds"] for row in actual_data}
except FileNotFoundError:
    st.warning("⚠️ Benchmark results (results.json) not found. Please run the measurements first.")
    actual = {}

# Load initial guesses when app starts
df = load_guesses()
leaderboard = compute_leaderboard(df, actual)

if not leaderboard.empty:
    st.dataframe(leaderboard, use_container_width=True)
else:
    st.warning("No data yet — waiting for form responses or benchmark results.")

# Button for manual refresh
if st.button("🔄 Refresh leaderboard"):
    df = load_guesses()
    leaderboard = compute_leaderboard(df, actual)
    st.success("Leaderboard refreshed!")
    st.dataframe(leaderboard, use_container_width=True)

st.divider()


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


