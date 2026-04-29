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


url = "https://oracleapex.com/ords/zahraa_individual_assignment/myapi/sales_per_region"

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
        regions = []
        categories = []
        clean_items = []

        for item in items:
            region = item.get("region_name")
            category = item.get("category_name")
            profit = item.get("total_profit")

            if region and category and profit is not None:
                profit_val = float(profit)

                clean_items.append({
                    "region": region,
                    "category": category,
                    "profit": profit_val
                })

                if region not in regions:
                    regions.append(region)
                if category not in categories:
                    categories.append(category)

        regions = sorted(regions)
        categories = sorted(categories)

        # BUILD MATRIX

        matrix = []
        for region in regions:
            row = []
            for category in categories:
                value = next(
                    (item["profit"] for item in clean_items
                     if item["region"] == region and item["category"] == category),
                    0.0
                )
                row.append(value)
            matrix.append(row)

        # BUILD LLM CONTEXT

        context = "Sales Profit by Region and Category:\n"

        for item in clean_items:
            context += f"{item['region']} - {item['category']}: ${item['profit']:,.2f}\n"

        # START LLM THREAD

        chat_thread = threading.Thread(
            target=start_chat,
            args=(context,),
            daemon=True
        )
        chat_thread.start()

        # CREATE HEATMAP

        fig, ax = plt.subplots(figsize=(12, 6))

        heatmap = ax.imshow(matrix, cmap="Blues", aspect="auto")

        # Color bar
        plt.colorbar(heatmap, ax=ax, label="Total Profit (USD)")

        # Axis labels
        ax.set_xticks(range(len(categories)))
        ax.set_yticks(range(len(regions)))

        ax.set_xticklabels(categories, rotation=45, ha="right")
        ax.set_yticklabels(regions)

        # Cell labels
        for i in range(len(regions)):
            for j in range(len(categories)):
                ax.text(
                    j, i,
                    f"${matrix[i][j]:,.0f}",
                    ha="center",
                    va="center",
                    fontsize=8
                )

        # Titles
        ax.set_title("Profit by Region and Product Category", fontsize=14, fontweight="bold")
        ax.set_xlabel("Product Category", fontsize=12)
        ax.set_ylabel("Region", fontsize=12)

        plt.tight_layout()
        plt.savefig("sales_per_region.png", dpi=150, bbox_inches="tight")
        # print("Chart saved!")

        plt.show()

else:
    print(f"Connection failed. Status code: {response.status_code}")
