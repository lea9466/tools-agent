import subprocess
import sys
from datetime import date


# ---------- פונקציות ----------

def get_date() -> str:
    return date.today().isoformat()


def run_python(code: str) -> str:
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except subprocess.TimeoutExpired:
        return "שגיאה: הקוד רץ יותר מ-10 שניות ונעצר."

    output = result.stdout
    if result.stderr:
        output += "\nשגיאה:\n" + result.stderr
    return output or "(הקוד רץ בלי להדפיס כלום)"


# ---------- סכמות ----------

GET_DATE_SCHEMA = {
    "type": "function",
    "name": "get_date",
    "description": "מחזיר את התאריך של היום בפורמט YYYY-MM-DD.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    },
    "strict": True,
}

RUN_PYTHON_SCHEMA = {
    "type": "function",
    "name": "run_python",
    "description": "מריץ קוד Python ומחזיר את מה שהודפס. חובה להשתמש ב-print כדי לראות תוצאה.",
    "parameters": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "קוד Python מלא להרצה",
            },
        },
        "required": ["code"],
        "additionalProperties": False,
    },
    "strict": True,
}


# ---------- registry ----------

tools_registry = {
    "get_date": get_date,
    "run_python": run_python,
}

tools = [GET_DATE_SCHEMA, RUN_PYTHON_SCHEMA]


# ---------- בדיקה (רצה רק עם python tools.py) ----------
if __name__ == "__main__":
    print(get_date())
    print(run_python("print(2 ** 100)"))
    print(run_python("print(1/1)"))

