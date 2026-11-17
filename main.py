import os
import json
import truststore
from dotenv import load_dotenv
from openai import OpenAI

from tools import tools, tools_registry


# Use the Windows certificate store (fixes SSL errors behind filters/proxies such as NetFree)
truststore.inject_into_ssl()

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o-mini"
MAX_STEPS = 5


SYSTEM_PROMPT = (
    "אתה עוזר קוד שעונה בעברית. יש לך כלי run_python שמריץ קוד על המחשב של המשתמש "
    "ויש לו גישה לקבצים בתיקייה הנוכחית. כשמבקשים ממך לעשות משהו שאפשר לעשות בקוד, "
    "השתמש בכלי ואל תגיד שאין לך גישה. "
    "אל תבקש מהמשתמש אישור לפני הפעלת הכלי, כי המערכת כבר מציגה לו את הקוד ומבקשת אישור לפני כל הרצה. "
    "אסור לך להריץ קוד זדוני."
)


if __name__ == "__main__":
    messages = []

    while True:
        question = input("\nאת (q ליציאה): ")
        if question == "q":
            break

        messages.append({"role": "user", "content": question})

        index = 0
        while index < MAX_STEPS:
            index += 1  
            response = client.responses.create(
                model=MODEL,
                instructions=SYSTEM_PROMPT,
                input=messages,
                tools=tools,
            )
            messages += response.output

            function_calls = [item for item in response.output if item.type == "function_call"]

            if not function_calls:
                print("\n🤖", response.output_text)
                break

            for call in function_calls:
                func = tools_registry[call.name]
                args = json.loads(call.arguments)
                approved = True
                if call.name == "run_python":
                    print("\n📝 הקוד שהמודל רוצה להריץ:")
                    print(args["code"])
                    approved = input("🔧 לאשר הרצה? (y/n): ").lower() == "y"
                if approved:
                    result = func(**args)
                else:
                    result = "המשתמש סירב להריץ את הקוד."

                print(f"🔧 {call.name} → {result}")
                messages.append({
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": result,
                })
        else:
            print("\n⛔ הגענו למגבלת הצעדים, עוצר.")




