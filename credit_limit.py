import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import requests
import threading


# LLM FUNCTION (Ollama - qwen3.5:2b)

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


url = "https://oracleapex.com/ords/zahraa_individual_assignment/myapi/credit_limit"

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
        years = []
        customers = []

        for item in items:
            year = item.get("order_year")
            customer = item.get("customers_exceeding_limit")

            if year is not None and customer is not None:
                years.append(str(year))
                customers.append(int(customer))

        # BUILD LLM CONTEXT

        context = "Customers Exceeding Credit Limit Per Year:\n"

        for y, c in zip(years, customers):
            context += f"Year {y}: {c} customers\n"

        # START LLM THREAD

        chat_thread = threading.Thread(
            target=start_chat,
            args=(context,),
            daemon=True
        )
        chat_thread.start()

        # CREATE BAR CHART

        fig, ax = plt.subplots(figsize=(10, 6))

        bars = ax.barh(years, customers, color="steelblue", edgecolor="white", height=0.6)

        # Add value labels at the end of each bar
        for bar in bars:
            width = bar.get_width()
            if width > 0:
                ax.text(
                    width + 0.3, bar.get_y() + bar.get_height() / 2,
                    str(int(width)),
                    va="center", ha="left", fontsize=11, fontweight="bold"
                )

        # Titles
        ax.set_xlabel("Number of Customers Exceeding Credit Limit", fontsize=12, labelpad=10)
        ax.set_ylabel("Year", fontsize=12, labelpad=10)
        ax.set_title("Customers Exceeding Credit Limit Per Year", fontsize=14, fontweight="bold", pad=15)

        ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
        ax.tick_params(axis="both", labelsize=11)
        ax.set_xlim(0, max(customers) * 1.15)

        ax.xaxis.grid(True, linestyle="--", alpha=0.5)
        ax.set_axisbelow(True)
        ax.spines[["top", "right"]].set_visible(False)

        plt.tight_layout()
        plt.savefig("credit_limit.png", dpi=150, bbox_inches="tight")

        plt.show()

else:
    print(f"Connection failed. Status code: {response.status_code}")
