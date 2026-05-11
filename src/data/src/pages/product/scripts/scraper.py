import json
import time
import random
import requests
from bs4 import BeautifulSoup

# Multi-Agent Προσέγγιση: Εναλλαγή "Ταυτότητας" για αποφυγή IP Bans
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
]

def get_price(url):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    try:
        # Rate Limiting: Τυχαία παύση 3 έως 8 δευτερόλεπτα (Προσομοίωση ανθρώπου)
        time.sleep(random.uniform(3.0, 8.0))
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Εδώ ψάχνουμε το DOM. Αλλάζεις την κλάση ανάλογα με το site στόχο.
        price_element = soup.find('span', class_='price-value') 
        
        if price_element:
            return price_element.text.strip()
        else:
            return "Ελέγξτε διαθεσιμότητα"
            
    except requests.exceptions.RequestException as e:
        # Error Handling: Δεν κρασάρει το σύστημα, απλά γυρνάει ασφαλές λεκτικό
        print(f"Σφάλμα σύνδεσης στο {url}: {e}")
        return "Ελέγξτε διαθεσιμότητα"

def run_update():
    # Διαβάζει το τοπικό JSON
    with open('src/data/smartphones.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    for item in data:
        if 'source_url' in item:
            print(f"Σάρωση για: {item['name']}...")
            new_price = get_price(item['source_url'])
            
            # Αν δεν βρει τιμή, κρατάει την παλιά (Προστασία Δεδομένων)
            if new_price != "Ελέγξτε διαθεσιμότητα":
                item['price'] = new_price

    # Αποθηκεύει τις νέες τιμές στο JSON
    with open('src/data/smartphones.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        print("Το JSON ενημερώθηκε επιτυχώς!")

if __name__ == "__main__":
    run_update()
