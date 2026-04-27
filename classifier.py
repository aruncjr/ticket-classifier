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

# 3 default sample messages
DEFAULT_MESSAGES = [
    "My payment got deducted but service is not activated",
    "App crashes every time I login",
    "How to change my email address?"
]


def classify_message(message):
    prompt = f"""You are a support ticket classifier.
Classify the given message into:
- Category: Billing, Technical Issue, Account, General Inquiry
- Priority: High (urgent/blocking), Medium (moderate), Low (general/informational)

Return ONLY valid JSON in this exact format with no extra text:
{{
  "category": "",
  "priority": ""
}}

Message: "{message}"
"""
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        raw = response.choices[0].message.content.strip()
        result = json.loads(raw)
        return {
            "message": message,
            "category": result.get("category", "Unknown"),
            "priority": result.get("priority", "Unknown"),
            "status": "success"
        }
    except json.JSONDecodeError:
        return {"message": message, "category": "Error", "priority": "Error", "status": "error", "note": "AI returned invalid JSON"}
    except Exception as e:
        return {"message": message, "category": "Error", "priority": "Error", "status": "error", "note": str(e)}


def print_header():
    print("\n" + "=" * 60)
    print("   🎫  SUPPORT TICKET CLASSIFIER")
    print("=" * 60)


def show_main_menu():
    print("\n   📋  How would you like to input messages?\n")
    print("   [1]  Type messages separated by commas")
    print("   [2]  Use the 3 default sample messages")
    print("   [Q]  Quit")
    print("\n" + "=" * 60)


def get_custom_messages():
    print("\n   📝  Enter your messages separated by commas.")
    print("   Example: My payment failed, App crashes, How to reset password\n")

    while True:
        raw = input("  👉 Your messages: ").strip()

        if not raw:
            print("  ⚠️  Please enter at least one message.\n")
            continue

        messages = [msg.strip() for msg in raw.split(",") if msg.strip()]

        if len(messages) == 0:
            print("  ⚠️  No valid messages found. Try again.\n")
            continue

        print(f"\n  ✅ {len(messages)} message(s) accepted.\n")
        return messages


def show_default_menu():
    print("\n   📋  Select from default messages:\n")
    for i, msg in enumerate(DEFAULT_MESSAGES, start=1):
        print(f"   [{i}]  {msg}")
    print(f"\n   [A]  Classify ALL 3 messages")
    print(f"   [B]  Go back")
    print("\n" + "=" * 60)

    while True:
        raw = input("\n  👉 Enter your choice (1, 2, 3 or A or B): ").strip().upper()

        if raw == "B":
            return None  # go back to main menu

        if raw == "A":
            print(f"\n  ✅ All 3 messages selected.\n")
            return DEFAULT_MESSAGES

        try:
            choices = [int(x.strip()) for x in raw.split(",")]
            invalid = [c for c in choices if c < 1 or c > len(DEFAULT_MESSAGES)]

            if invalid:
                print(f"  ⚠️  Invalid choice(s): {invalid}. Please enter 1, 2, or 3 only.")
                continue

            selected = [DEFAULT_MESSAGES[c - 1] for c in choices]
            print(f"\n  ✅ {len(selected)} message(s) selected.\n")
            return selected

        except ValueError:
            print("  ⚠️  Invalid input. Enter 1, 2, 3 or A for all or B to go back.")


def get_user_selection():
    while True:
        show_main_menu()
        choice = input("\n  👉 Enter your choice (1, 2 or Q): ").strip().upper()

        if choice == "Q":
            print("\n  👋 Goodbye!\n")
            exit()

        elif choice == "1":
            return get_custom_messages()

        elif choice == "2":
            result = show_default_menu()
            if result is not None:
                return result
            # if None, loop back to main menu

        else:
            print("  ⚠️  Invalid choice. Please enter 1, 2, or Q.")


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
        selected_messages = get_user_selection()
        results = classify_all(selected_messages)
        print_summary(results)

        clean_output = [
            {"message": r["message"], "category": r["category"], "priority": r["priority"]}
            for r in results
        ]
        with open("output.json", "w") as f:
            json.dump(clean_output, f, indent=2)

        print(f"\n   💾 Results saved to output.json")
        input("\n   ⌨️  Press Enter to return to menu...")
