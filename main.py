import threading
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")

from data_fetch import fetch_credit_limit_data, fetch_average_order_data
from visualisation import plot_credit_limit, plot_average_order
from llm import run_llm_interface

def main():
    print("Fetching data from API...")
    credit_items = fetch_credit_limit_data()
    order_items = fetch_average_order_data()

    if not credit_items or not order_items:
        print("Failed to fetch data. Exiting.")
        return

    print("Data fetched successfully!")

    # Run LLM in background thread
    llm_thread = threading.Thread(
        target=run_llm_interface,
        args=(credit_items, order_items),
        daemon=True
    )
    llm_thread.start()

    # Show both charts without blocking
    plot_credit_limit(credit_items)
    plot_average_order(order_items)

    # Keep charts open while LLM runs
    plt.pause(0.1)
    llm_thread.join()

if __name__ == "__main__":
    main()