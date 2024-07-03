import frappe
from urllib.parse import urlencode
import requests


def woo_authendication():
    url = "https://theshadingcompany.ae/wp-json/wc/v3/products/15941"

    # WooCommerce Consumer Key and Secret
    consumer_key = "ck_ab947471934255ae856493bd3677c0598532ec59"
    consumer_secret = "cs_e8349c5862b7fca810342be4d3392abc6ef93081"

    # Data to be updated
    data = {
        "regular_price": "24.54"
    }

    # Make the PUT request to update the product
    response = requests.put(url, auth=(consumer_key, consumer_secret), json=data)

    # Check the response
    if response.status_code == 200:
        print("Product updated successfully.")
        print(response.json())
    else:
        print(f"Failed to update product. Status code: {response.status_code}")
        print(response.text)