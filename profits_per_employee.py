import matplotlib.pyplot as plt
import requests
import numpy as np
import threading


# LLM FUNCTION (Ollama - Gemma 2B)

def query_ollama(context, question):
    try:
        url = "http://localhost:11434/api/generate"

        prompt = f"""
You are a data analyst assistant.

ONLY answer questions related to the dataset below.
If the question is unrelated, respond with:
"I can only answer questions related to the dataset."

DATASET:
{context}

QUESTION:
{question}

ANSWER:
"""

        payload = {
            "model": "gemma:2b",   
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(url, json=payload, timeout=180)

        #  BETTER ERROR DEBUGGING
        if response.status_code != 200:
            return f"Error {response.status_code}: {response.text}"

        result = response.json()
        return result.get("response", "No response from model")

    except Exception as e:
        return f"Exception: {str(e)}"



# INTERACTIVE CHAT THREAD

def start_chat(context):
    print("\nLLM Assistant Ready. Ask questions about the dataset.")
    print("Type 'exit' to stop.\n")

    while True:
        question = input("Ask: ")

        if question.lower() == "exit":
            break

        answer = query_ollama(context, question)
        print("Answer:", answer, "\n")



# Fetch data from API

url = "https://oracleapex.com/ords/zahraa_individual_assignment/myapi/profits_per_employee"

headers = {
    "Accept": "application/json",
    "Host": "oracleapex.com",
    "User-Agent": "Mozilla/5.0 Firefox/149.0"
}

response = requests.get(url, headers=headers, timeout=30)


# Extract data

if response.status_code == 200:
    print("Connection successful!")
    data = response.json()

    items = data.get("items", [])

    if not items:
        print("No data returned from API")
    else:
        employees = []
        profits = []

        for item in items:
            name = item.get("employee_name")
            profit_val = item.get("total_profit")

            if name is not None and profit_val is not None:
                # Handle both string and numeric values safely
                if isinstance(profit_val, str):
                    profit_clean = profit_val.strip().replace('$', '').replace(',', '')
                    try:
                        profit = float(profit_clean)
                    except:
                        continue
                else:
                    profit = float(profit_val)

                employees.append(name)
                profits.append(profit)


        # BUILD DATA CONTEXT FOR LLM

        context = "Employee Profit Data:\n"
        for e, p in zip(employees, profits):
            context += f"{e}: ${p:,.2f}\n"


        # START LLM THREAD

        chat_thread = threading.Thread(target=start_chat, args=(context,), daemon=True)
        chat_thread.start()


        # Create horizontal bar chart

        fig, ax = plt.subplots(figsize=(10, 8))
        bars = ax.barh(employees, profits, color='steelblue', edgecolor='navy', alpha=0.8)

        # Add value labels
        for bar, profit in zip(bars, profits):
            ax.text(
                bar.get_width() + 5000,
                bar.get_y() + bar.get_height()/2,
                f'${profit:,.0f}',
                va='center',
                fontsize=9
            )

        # Customize
        ax.set_xlabel('Total Profit ($)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Employee Name', fontsize=12, fontweight='bold')
        ax.set_title('Employee Profit Performance', fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3, linestyle='--')

        if profits:
            ax.set_xlim(0, max(profits) * 1.1)

        plt.tight_layout()
        plt.show()

else:
    print(f"Connection failed. Status code: {response.status_code}")
