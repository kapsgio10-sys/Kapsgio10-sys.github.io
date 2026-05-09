import os
from pathlib import Path
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

current_html = Path("index.html").read_text(encoding="utf-8")

prompt = f"""
Είσαι senior web engineer και product designer.
Αναβάθμισε το ελληνικό marketplace site ReGadget Market.

Επέστρεψε ΜΟΝΟ ένα πλήρες έγκυρο index.html αρχείο.
Μην βάλεις markdown. Μην βάλεις εξηγήσεις.

Απαραίτητα:
- Ελληνική γλώσσα
- Premium marketplace αισθητική
- Responsive mobile-first design
- Hero, αγγελίες, αναζήτηση, φίλτρα, φόρμα πώλησης, επικοινωνία
- JavaScript μέσα στο ίδιο HTML
- Να μη φαίνεται κανένα API key
- Να παραμένει static site για GitHub Pages
- Χρησιμοποίησε Tailwind CDN

Τρέχον index.html:
{current_html}
"""

response = client.responses.create(
    model="gpt-4.1-mini",
    input=prompt,
)

html = response.output_text.strip()

if not (html.lower().startswith("<!doctype html") or html.lower().startswith("<html")):
    raise RuntimeError("Το AI δεν επέστρεψε έγκυρο HTML")

Path("index.html").write_text(html, encoding="utf-8")

print("Το index.html αναβαθμίστηκε από AI.")
