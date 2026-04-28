import ollama

def build_data_context(credit_items, order_items):
    context = "You are a data analyst assistant for OT (a trading company). "
    context += "You have access to the following business data and must only answer questions related to this data. "
    context += "If a question is not related to this data, politely decline to answer.\n\n"

    context += "=== Customers Exceeding Credit Limit Per Year ===\n"
    for item in credit_items:
        year = item.get("order_year")
        customers = item.get("customers_exceeding_limit")
        context += f"Year {year}: {customers} customers exceeded their credit limit\n"

    context += "\n=== Average Order Value Per Month (2017) ===\n"
    for item in order_items:
        month = item.get("month_name")
        value = item.get("avg_order_value")
        context += f"{month}: ${float(value):,.2f} average order value\n"

    return context


def run_llm_interface(credit_items, order_items):
    print("\n" + "="*50)
    print("OT Data Assistant - Ask me anything about the data!")
    print("Type 'exit' to quit")
    print("="*50 + "\n")

    data_context = build_data_context(credit_items, order_items)

    conversation_history = []

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        if not user_input:
            continue

        conversation_history.append({
            "role": "user",
            "content": user_input
        })

        try:
            response = ollama.chat(
                model="qwen3.5:2b",
                messages=[
                    {
                        "role": "system",
                        "content": data_context
                    }
                ] + conversation_history
            )

            assistant_message = response["message"]["content"]
            print(f"\nAssistant: {assistant_message}\n")

            conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

        except Exception as e:
            print(f"Error communicating with Ollama: {e}")
            print("Make sure Ollama is running in the background.\n")