# --- Standard Library Imports ---
import ast
import json
import os
import re
import subprocess
import time

# --- Third-Party Library Imports ---
import requests
from canvasapi import Canvas
from dotenv import find_dotenv, load_dotenv
from langchain_openai import ChatOpenAI

# --- Load Environment Variables ---
load_dotenv()

# --- Environment Variable Configuration ---
data_dir = os.environ.get("DATA_DIR", "MathTHPT2025")
loading_folder_env = os.environ.get(
    "LOADING_FOLDER",
    '["1.Chuyen de", "2.De chac diem 8", "3.De chac diem 9", "4.De luyen them", "5.De quan trong", "6.De so"]',
)
try:
    loading_folder = json.loads(loading_folder_env)
except Exception:
    try:
        loading_folder = ast.literal_eval(loading_folder_env)
    except Exception:
        loading_folder = [
            s.strip() for s in re.split(r"[;,]", loading_folder_env) if s.strip()
        ]

# --- API Keys and Configuration ---
api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")
model_name = os.getenv("OPENAI_MODEL_NAME")

if not all([api_key, api_base, model_name]):
    raise RuntimeError(
        "Check .env file and ensure that it exists and that OPENAI_API_KEY, "
        "OPENAI_API_BASE, and OPENAI_MODEL_NAME variables are set."
    )

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
PART_USED = os.getenv("PART_USED")
COURSE_ID = os.getenv("COURSE_ID")

print(model_name)
print(loading_folder)

# --- OpenAI LLM Initialization ---
llm = ChatOpenAI(
    model_name=model_name,
    openai_api_key=api_key,
    openai_api_base=api_base,
    max_tokens=None,
    max_retries=2,
    temperature=0.69,
)

# --- Function to Ask OpenAI ---
def ask(request):
    try:
        response = llm.invoke(request)
        return response
    except Exception as e:
        print(request)
        raise RuntimeError(f"Error when calling openAI: {e}")

# --- Prompt Loading ---
prompt = None
candidates = ["prompt.txt"]
seen = set()
candidates = [p for p in candidates if p and not (p in seen or seen.add(p))]

for p in candidates:
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as _f:
            prompt = _f.read()
        print(f"Loaded prompt from: {p}")
        break
else:
    print("prompt.txt not found; prompt is None.")

print(prompt)
print(loading_folder)

# --- Main Processing Loop ---
for folder in loading_folder:
    pdf_files = []
    folder_path = os.path.join(data_dir, folder)
    for file in os.listdir(folder_path):
        if file.lower().endswith(".pdf"):
            file = os.path.splitext(file)[0]
            pdf_files.append(file)
            file_path = os.path.abspath(os.path.join(folder_path, file))
            final_md_path = os.path.join(file_path, "output", "final.md")
            print(final_md_path)
            final_md_str = None
            if os.path.exists(final_md_path):
                with open(final_md_path, "r", encoding="utf-8") as f:
                    final_md_str = f.read()
            else:
                alt_md_path = os.path.splitext(file_path)[0] + ".md"
                if os.path.exists(alt_md_path):
                    with open(alt_md_path, "r", encoding="utf-8") as f:
                        final_md_str = f.read()
            try:
                response = ask(prompt + "\n\n" + final_md_str)
            except Exception as e:
                print("error prompting file", final_md_path)
                continue
            out_dir = os.path.dirname(final_md_path)
            os.makedirs(out_dir, exist_ok=True)
            base_name = os.path.splitext(os.path.basename(final_md_path))[0]
            out_path = os.path.join(out_dir, f"{base_name}.text2qti.txt")

            text = ""
            if response is None:
                text = ""
            elif isinstance(response, str):
                text = response
            else:
                if hasattr(response, "content"):
                    text = response.content
                elif hasattr(response, "text"):
                    text = response.text
                else:
                    choices = getattr(response, "choices", None)
                    if choices:
                        first = choices[0]
                        if isinstance(first, dict):
                            text = (
                                first.get("message", {}).get("content")
                                or first.get("text", "")
                                or ""
                            )
                        else:
                            text = (
                                getattr(first, "message", None)
                                or getattr(first, "text", None)
                                or str(first)
                            )
                    else:
                        text = str(response)

            with open(out_path, "w", encoding="utf-8") as out_f:
                out_f.write(text or "")

            print(f"Wrote output to: {out_path}")
            print()

# --- Function to Upload QTI to Canvas ---
def upload_qti_to_canvas(file_path: str):
    payload = {
        "migration_type": "qti_converter",
        "pre_attachment": {"name": "final.text2qti.zip"},
        "settings": {"import_quizzes_next": False},
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        f"{API_URL}/api/v1/courses/{COURSE_ID}/content_migrations/",
        headers=headers,
        data=json.dumps(payload),
    )
    response.raise_for_status()
    migration = response.json()
    upload_url = migration["pre_attachment"]["upload_url"]
    upload_params = migration["pre_attachment"]["upload_params"]

    with open(file_path, "rb") as file:
        files = {"file": (upload_params["Filename"], file)}
        upload_response = requests.post(upload_url, data=upload_params, files=files)
        upload_response.raise_for_status()

    progress_url = migration["progress_url"]
    while True:
        progress_response = requests.get(progress_url, headers=headers)
        progress_response.raise_for_status()
        progress = progress_response.json()
        print(f"\rMigration progress: {progress['completion']}%", end="")
        if progress["workflow_state"] == "completed":
            print("\nMigration completed successfully.")
            break
        elif progress["workflow_state"] == "failed":
            print("\nMigration failed.")
            return None
        time.sleep(3)

    canvas = Canvas(API_URL, API_KEY)
    course = canvas.get_course(COURSE_ID)
    quizzes = course.get_quizzes()

    base_name = f"[{folder}]"
    matching_quizzes = [q for q in quizzes if q.title.startswith(base_name)]

    if matching_quizzes:
        numbers = []
        for q in matching_quizzes:
            parts = q.title.split()
            try:
                numbers.append(int(parts[-1]))
            except ValueError:
                pass
        next_num = max(numbers) + 1 if numbers else 1
    else:
        next_num = 1

    new_quiz = max(quizzes, key=lambda q: q.id, default=None)

    if new_quiz:
        new_title = f"{base_name} {base}"
        new_quiz.edit(quiz={"title": new_title})
        print(f"Renamed quiz: {new_title}")

        new_quiz.edit(quiz={"published": True})
        print("Quiz has been published.")

        return f"{API_URL}/courses/{COURSE_ID}/quizzes/{new_quiz.id}"
    else:
        print("No new quiz was created.")
        return None

# --- Process text2qti ---
for folder in loading_folder:
    folder_path = os.path.join(data_dir, folder)
    if not os.path.isdir(folder_path):
        print(f"Skipping missing folder: {folder_path}")
        continue

    for fname in os.listdir(folder_path):
        if not fname.lower().endswith(".pdf"):
            continue

        base = os.path.splitext(fname)[0]
        file_path = os.path.abspath(os.path.join(folder_path, base))
        final_md_path = os.path.join(file_path, "output", "final.md")
        out_dir = os.path.dirname(final_md_path)
        base_name = os.path.splitext(os.path.basename(final_md_path))[0]
        out_path = os.path.join(out_dir, f"{base_name}.text2qti.txt")

        if not os.path.exists(out_path):
            print(f"No text2qti output for: {out_path}")
            continue

        cmd = ["text2qti", out_path]
        print(f"Running: {' '.join(cmd)}")
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode == 0:
                print(f"Success for {out_path}")
                if proc.stdout:
                    print("stdout:", proc.stdout.strip())
            else:
                print(f"Command failed (code={proc.returncode}) for {out_path}")
                if proc.stdout:
                    print("stdout:", proc.stdout.strip())
                if proc.stderr:
                    print("stderr:", proc.stderr.strip())
        except FileNotFoundError:
            print("Command `text2qti` not found. Ensure it's installed and on PATH.")
            break
        except Exception as e:
            print(f"Error running text2qti on {out_path}: {e}")
            continue
        """
        zip_path = os.path.join(file_path, "output", "final.text2qti.zip")
        if os.path.exists(zip_path):
            try:
                result = upload_qti_to_canvas(zip_path)
                if result:
                    print("Uploaded QTI:", result)
                else:
                    print("Upload completed but no quiz URL returned.")
            except Exception as e:
                print(f"Upload failed for {zip_path}: {e}")
        else:
            print(f"QTI zip not found: {zip_path}")
        #"""