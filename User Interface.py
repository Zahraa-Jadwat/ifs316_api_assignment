import requests
import tkinter as tk
from tkinter import scrolledtext
import threading

# -------------------------------
# LLM FUNCTION (Ollama - qwen3.5:2b)
# -------------------------------
def query_ollama(context, question):
    try:
        url = "http://localhost:11434/api/generate"

        prompt = f"""
You are a data analyst assistant.

ONLY answer questions related to the datasets below:
- Average order value
- Best product categories
- Credit limit
- Orders per region
- Profit per region

If the question is unrelated, respond with:
"I can only answer questions related to the dataset."

DATASETS:
{context}

QUESTION:
{question}

ANSWER:
"""

        payload = {
            "model": "qwen3.5:2b",
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(url, json=payload, timeout=180)

        if response.status_code != 200:
            return f"Error {response.status_code}: {response.text}"

        return response.json().get("response", "No response")

    except Exception as e:
        return f"Error: {str(e)}"


# -------------------------------
# FETCH ALL DATA (YOUR STRUCTURE KEPT)
# -------------------------------
def fetch_all_data():
    context = ""

    headers = {
        "Accept": "application/json",
        "Host": "oracleapex.com",
        "User-Agent": "Mozilla/5.0"
    }

    # 1. Average Order Value
    url = "https://oracleapex.com/ords/zahraa_individual_assignment/myapi/average_order_value"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        items = res.json().get("items", [])
        context += "\nAverage Order Value:\n"
        for i in items:
            context += f"{i['month_name']}: ${float(i['avg_order_value']):,.2f}\n"

    # 2. Best Product Categories
    url = "https://oracleapex.com/ords/zahraa_individual_assignment/myapi/best_product_categories"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        items = res.json().get("items", [])
        context += "\nBest Product Categories:\n"
        for i in items:
            context += f"{i['category_name']}: ${float(i['total_profit']):,.2f}\n"

    # 3. Credit Limit
    url = "https://oracleapex.com/ords/zahraa_individual_assignment/myapi/credit_limit"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        items = res.json().get("items", [])
        context += "\nCredit Limit:\n"
        for i in items:
            context += f"Year {i['order_year']}: {i['customers_exceeding_limit']} customers\n"

    # 4. Orders per Region
    url = "https://oracleapex.com/ords/zahraa_individual_assignment/myapi/sales_per_region"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        items = res.json().get("items", [])
        context += "\nOrders per Region:\n"
        for i in items:
            context += f"{i['region_name']} - {i['category_name']}: ${float(i['total_profit']):,.2f}\n"

    # 5. Profit per Region (Employee)
    url = "https://oracleapex.com/ords/zahraa_individual_assignment/myapi/profits_per_employee"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        items = res.json().get("items", [])
        context += "\nProfit per Employee:\n"
        for i in items:
            context += f"{i['employee_name']}: ${float(i['total_profit']):,.2f}\n"

    return context


# -------------------------------
# UI FUNCTION (CHATGPT STYLE)
# -------------------------------
def create_ui(context):

    def send_message():
        user_msg = entry.get()
        if not user_msg.strip():
            return

        chat_box.insert(tk.END, f"\nYou: {user_msg}\n", "user")
        entry.delete(0, tk.END)

        def get_response():
            response = query_ollama(context, user_msg)
            chat_box.insert(tk.END, f"Assistant: {response}\n", "bot")
            chat_box.yview(tk.END)

        threading.Thread(target=get_response).start()

    # WINDOW
    root = tk.Tk()
    root.title("Data Analyst Assistant")
    root.geometry("700x600")
    root.configure(bg="#0D1117")  # black

    # HEADER
    header = tk.Label(
        root,
        text="Hello 👋\nYou can ask questions about:\nAverage Order Value, Best Product Categories,\nCredit Limit, Orders per Region, Profit per Region",
        bg="#0D1117",
        fg="#58A6FF",
        font=("Arial", 12),
        justify="center"
    )
    header.pack(pady=10)

    # CHAT BOX
    chat_box = scrolledtext.ScrolledText(
        root,
        wrap=tk.WORD,
        bg="#161B22",
        fg="white",
        font=("Arial", 10)
    )
    chat_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    chat_box.tag_config("user", foreground="#58A6FF")
    chat_box.tag_config("bot", foreground="white")

    # INPUT FIELD
    entry = tk.Entry(
        root,
        bg="#21262D",
        fg="white",
        insertbackground="white",
        font=("Arial", 11)
    )
    entry.pack(fill=tk.X, padx=10, pady=5)

    # SEND BUTTON
    send_btn = tk.Button(
        root,
        text="Send",
        command=send_message,
        bg="#238636",
        fg="white"
    )
    send_btn.pack(pady=5)

    root.mainloop()


# -------------------------------
# MAIN
# -------------------------------
if __name__ == "__main__":
    print("Fetching data from APIs...")
    context_data = fetch_all_data()

    print("Launching UI...")
    create_ui(context_data)
