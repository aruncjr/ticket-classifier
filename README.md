# Support Ticket Classifier

An AI-powered tool that automatically classifies customer support messages by **category** and **priority** using the OpenAI API.

---

## What it does

Takes a list of customer messages → sends each one to OpenAI → returns structured JSON with category and priority assigned.

**Categories:** Billing, Technical Issue, Account, General Inquiry  
**Priority Levels:** High, Medium, Low

---

## Sample Output

```json
[
  {
    "message": "My payment got deducted but service is not activated",
    "category": "Billing",
    "priority": "High"
  },
  {
    "message": "App crashes every time I login",
    "category": "Technical Issue",
    "priority": "High"
  },
  {
    "message": "How to change my email address?",
    "category": "Account",
    "priority": "Low"
  }
]
```

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/your-username/ticket-classifier.git
cd ticket-classifier
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your OpenAI API key
```bash
cp .env.example .env
```
Open `.env` and replace `your-api-key-here` with your actual key from https://platform.openai.com/api-keys

### 4. Run the classifier
```bash
python classifier.py
```

Results are printed to the console and saved to `output.json`.

---

## How to add your own messages

Open `classifier.py` and edit the `messages` list at the top:

```python
messages = [
    "My payment got deducted but service is not activated",
    "App crashes every time I login",
    "How to change my email address?"
    # Add more messages here
]
```

---

---

## Approach

1. Each message is sent individually to Groq's `llama-3.1-8b-instant` model
2. The prompt instructs the model to return ONLY valid JSON (no extra text)
3. `temperature=0` is used for consistent, deterministic results
4. Error handling covers invalid JSON responses and API failures
5. All results are collected into a list and saved as `output.json`

> [!NOTE]
> Originally designed for OpenAI. Switched to Groq (LLaMA 3.1) due to API credit constraints — the prompt and JSON output format remain identical.

---

## Project Structure

```
ticket-classifier/
├── classifier.py       # Main script (using Groq)
├── .env.example        # API key template (rename to .env)
├── requirements.txt    # Python dependencies
├── output.json         # Generated output (created on run)
├── README.md           # This file
└── .env               # Your local keys (ignored by git)
```

---

## Tools Used

- Python 3.8+
- Groq API (llama-3.1-8b-instant)
- python-dotenv (for secure API key loading)
