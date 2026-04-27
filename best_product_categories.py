import requests
import matplotlib.pyplot as plt

# Oracle APEX API endpoint
url = "https://oracleapex.com/ords/zahraa_individual_assignment/myapi/best_product_categories"

headers = {
    "Accept": "application/json",
    "Host": "oracleapex.com",
    "User-Agent": "Mozilla/5.0 Firefox/149.0"
}

# Fetch data from API
response = requests.get(url, headers=headers, timeout=30)

# Extract items
if response.status_code == 200:
    print("Connection successful!")
    data = response.json()

    # Safe access to items
    items = data.get("items", [])

    if not items:
        print("No data returned from API")
    else:
        # Safe loop extraction
        categories = []
        profits = []

        for item in items:
            category = item.get("category_name")
            profit = item.get("total_profit")

            if category is not None and profit is not None:
                categories.append(category)
                profits.append(float(profit))

        # Create Pie Chart
        plt.figure()

        plt.pie(
            profits,
            labels=categories,
            autopct='%1.1f%%',
            startangle=140
        )

        plt.title("Best Product Categories by Profit")

        # Key / Legend
        plt.legend(categories, title="Categories", loc="center left", bbox_to_anchor=(1, 0.5))

        plt.tight_layout()
        plt.show()
else:
    print(f"Connection failed. Status code: {response.status_code}")
