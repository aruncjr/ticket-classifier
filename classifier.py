import os
import json
import time
import sys
from groq import Groq
from dotenv import load_dotenv

# Fix for Windows emoji printing
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PRIORITY_ICONS = {
    "High":   "🔴 HIGH",
    "Medium": "🟡 MEDIUM",
    "Low":    "🟢 LOW"
}

CATEGORY_ICONS = {
    "Billing":         "💳 Billing",
    "Technical Issue": "🛠  Technical Issue",
    "Account":         "👤 Account",
    "General Inquiry": "💬 General Inquiry"
}

# ----------------------------
# Only these 3 messages
# ----------------------------
ALL_MESSAGES = [
    "My payment got deducted but service is not activated",
    "App crashes every time I login",
    "How to change my email address?"
]


def classify_message(message):#Promt Engineering , tell Ai about the messages
    prompt = f"""You are a support ticket classifier.
Classify the given message into:
- Category: Billing, Technical Issue, Account, General Inquiry
- Priority: High (urgent/blocking), Medium (moderate), Low (general/informational)

Return ONLY valid JSON in this exact format with no extra text:
{{
  "category": "",
  "priority": ""
}}

#sends user message to Groq model 
Message: "{message}" 
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        raw = response.choices[0].message.content.strip()
        result = json.loads(raw)#converts string to dictionary
        return {
            "message": message,
            "category": result.get("category", "Unknown"),
            "priority": result.get("priority", "Unknown"),
            "status": "success"
        }
    except json.JSONDecodeError:#if ai return
        return {"message": message, "category": "Error", "priority": "Error", "status": "error", "note": "AI returned invalid JSON"}
    except Exception as e:#General errors
        #handles API failures,No internet, invalid keys
        return {"message": message, "category": "Error", "priority": "Error", "status": "error", "note": str(e)}


def print_header():
    print("\n" + "=" * 60)
    print("   🎫  SUPPORT TICKET CLASSIFIER")
    print("=" * 60)

#shows Menu
def show_menu():
    print("\n   📋  Choose a message to classify:\n")
    for i, msg in enumerate(ALL_MESSAGES, start=1):
        print(f"   [{i}]  {msg}")
    print(f"\n   [A]  Classify ALL messages")
    print(f"   [Q]  Quit")
    print("\n" + "=" * 60)


def get_user_selection():
    while True:
        try:
            raw = input("\n  👉 Enter your choice (1, 2, 3 or A or Q): ").strip().upper()

            if raw == "Q":
                print("\n  👋 Goodbye!\n")
                exit()

            if raw == "A":
                print(f"\n  ✅ All {len(ALL_MESSAGES)} messages selected.\n")
                return ALL_MESSAGES

            # Allow comma-separated choices like "1,2"
            choices = [int(x.strip()) for x in raw.split(",") if x.strip().isdigit()]
            invalid = [c for c in choices if c < 1 or c > len(ALL_MESSAGES)]

            if not choices:
                print("  ⚠️  Invalid input. Enter 1, 2, 3 or A for all or Q to quit.")
                continue

            if invalid:
                print(f"  ⚠️  Invalid choice(s): {invalid}. Please enter 1, 2, or 3 only.")
                continue

            selected = [ALL_MESSAGES[c - 1] for c in choices]
            print(f"\n  ✅ {len(selected)} message(s) selected.\n")
            return selected

        except ValueError:
            print("  ⚠️  Invalid input. Enter 1, 2, 3 or A for all or Q to quit.")
        except EOFError:
            exit()


def print_result(result, index):
    priority = result.get("priority", "Unknown")
    category = result.get("category", "Unknown")
    status   = result.get("status", "success")
    icon     = PRIORITY_ICONS.get(priority, "⚪ UNKNOWN")
    cat_icon = CATEGORY_ICONS.get(category, f"📁 {category}")
    msg_preview = result['message'][:50] + ('...' if len(result['message']) > 50 else '')

    print(f"  [{index}] Message  : {msg_preview}")
    if status == "error":
        print(f"       Status   : ❌ Error — {result.get('note', 'Unknown error')}")
    else:
        print(f"       Category : {cat_icon}")
        print(f"       Priority : {icon}")
        print(f"       Status   : ✅ Classified successfully")
    print()

#counts high,medium,low and errors
def print_summary(results):
    high   = sum(1 for r in results if r.get("priority") == "High")
    medium = sum(1 for r in results if r.get("priority") == "Medium")
    low    = sum(1 for r in results if r.get("priority") == "Low")
    errors = sum(1 for r in results if r.get("status") == "error")

    print("=" * 60)
    print("   📊  SUMMARY")
    print("=" * 60)
    print(f"   🔴 High priority    : {high}")
    print(f"   🟡 Medium priority  : {medium}")
    print(f"   🟢 Low priority     : {low}")
    if errors:
        print(f"   ❌ Errors          : {errors}")
    print(f"   ✅ Total processed  : {len(results)}")
    print("=" * 60)

#
def classify_all(messages):
    results = []
    print("=" * 60)
    print("   ⚙️   PROCESSING MESSAGES")
    print("=" * 60 + "\n")
    for i, msg in enumerate(messages, start=1):
        print(f"  ⏳ [{i}/{len(messages)}] Classifying...")
        start = time.time()
        result = classify_message(msg)
        elapsed = round(time.time() - start, 2)
        print(f"  ✅ Done in {elapsed}s\n")
        print_result(result, i)
        results.append(result)
    return results


if __name__ == "__main__":
    print_header()
    
    while True:
        show_menu()
        selected_messages = get_user_selection()
        
        results = classify_all(selected_messages)
        print_summary(results)

        # Append to output.json instead of overwriting completely if you prefer, 
        # but the prompt version overwrites with the latest session.
        clean_output = [
            {"message": r["message"], "category": r["category"], "priority": r["priority"]}
            for r in results
        ]
        with open("output.json", "w") as f:
            json.dump(clean_output, f, indent=2)

        print(f"\n   💾 Latest session saved to output.json")
        input("\n   ⌨️  Press Enter to return to menu...")
