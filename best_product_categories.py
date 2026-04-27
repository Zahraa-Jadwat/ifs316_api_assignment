import requests
import matplotlib.pyplot as plt

# Oracle APEX API endpoint
url = "https://oracleapex.com/ords/zahraa_individual_assignment/myapi/best_product_categories"

# Fetch data from API
response = requests.get(url)
data = response.json()

# Extract items
items = data["items"]

categories = [item["category_name"] for item in items]
profits = [item["total_profit"] for item in items]

# Create Pie Chart
plt.figure()

plt.pie(
    profits,
    labels=categories,
    autopct='%1.1f%%',
    startangle=140
)

plt.title("Best Product Categories by Profit")

# Key
plt.legend(categories, title="Categories", loc="center left", bbox_to_anchor=(1, 0.5))

plt.tight_layout()
plt.show()