import matplotlib.pyplot as plt
import requests
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
            "model": "qwen3.5:2b",
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(url, json=payload, timeout=180)

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


# FETCH DATA FROM API


url = "https://oracleapex.com/ords/zahraa_individual_assignment/myapi/best_product_categories"

headers = {
    "Accept": "application/json",
    "Host": "oracleapex.com",
    "User-Agent": "Mozilla/5.0 Firefox/149.0"
}

response = requests.get(url, headers=headers, timeout=30)

# PROCESS DATA


if response.status_code == 200:
    print("Connection successful!")
    data = response.json()

    items = data.get("items", [])

    if not items:
        print("No data returned from API")
    else:
        categories = []
        profits = []

        for item in items:
            category = item.get("category_name")
            profit = item.get("total_profit")

            if category is not None and profit is not None:
                categories.append(category)
                profits.append(float(profit))

        # BUILD LLM CONTEXT

        context = "Best Product Categories by Profit:\n"

        for c, p in zip(categories, profits):
            context += f"{c}: ${p:,.2f}\n"

        # START LLM THREAD

        chat_thread = threading.Thread(
            target=start_chat,
            args=(context,),
            daemon=True
        )
        chat_thread.start()

        # CREATE PIE CHART

        fig, ax = plt.subplots(figsize=(10, 7))

        ax.pie(
            profits,
            labels=categories,
            autopct="%1.1f%%",
            startangle=140
        )

        # Titles
        ax.set_title("Best Product Categories by Profit", fontsize=14, fontweight="bold")

        # Legend
        ax.legend(categories, title="Categories", loc="center left", bbox_to_anchor=(1, 0.5))

        plt.tight_layout()
        plt.savefig("best_product_categories.png", dpi=150, bbox_inches="tight")

        plt.show()

else:
    print(f"Connection failed. Status code: {response.status_code}")
