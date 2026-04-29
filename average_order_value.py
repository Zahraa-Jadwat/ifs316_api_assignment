import matplotlib.pyplot as plt
import requests
import threading


# LLM FUNCTION (Ollama - gemma2:2b)

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
            "model": "gemma2:2b",
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


url = "https://oracleapex.com/ords/zahraa_individual_assignment/myapi/average_order_value"

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
        months = []
        avg_order = []

        for item in items:
            month = item.get("month_name")
            value = item.get("avg_order_value")

            if month is not None and value is not None:
                months.append(month)
                avg_order.append(float(value))

        # BUILD LLM CONTEXT

        context = "Average Order Value per Month (2017):\n"

        for m, v in zip(months, avg_order):
            context += f"{m}: ${v:,.2f}\n"

        # START LLM THREAD

        chat_thread = threading.Thread(
            target=start_chat,
            args=(context,),
            daemon=True
        )
        chat_thread.start()

        # CREATE LINE CHART

        fig, ax = plt.subplots(figsize=(14, 6))

        ax.plot(
            months,
            avg_order,
            marker="o",
            linewidth=2,
            markersize=7,
            color="#2196F3",
            markerfacecolor="#FF5722"
        )

        # Titles
        ax.set_title("Average Order Value per Month (2017)", fontsize=14, fontweight="bold")
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("Average Order Value (USD)", fontsize=12)

        ax.tick_params(axis="x", rotation=45)
        ax.grid(axis="y", linestyle="--", alpha=0.5)

        plt.tight_layout()
        plt.savefig("average_order_value.png", dpi=150, bbox_inches="tight")

        plt.show()

else:
    print(f"Connection failed. Status code: {response.status_code}")
