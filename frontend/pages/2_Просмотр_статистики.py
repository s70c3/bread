import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# FastAPI URL
API_URL = "http://backend:8543"  # Update with your actual API URL

st.title("Production Aggregation Results")

# Sidebar inputs for query parameters
st.sidebar.header("Параметры запроса статистики")
start_period = st.sidebar.date_input("Начало периода", datetime.now() - timedelta(days=1))
end_period = st.sidebar.date_input("Конец периода", datetime.now())
step = st.sidebar.number_input("Шаг (минут)", min_value=1, value=60)

# Make a GET request to the /count/ endpoint
response = requests.get("http://backend:8543/count/")

# Check if the request was successful
if response.status_code == 200:
    # Get the counting requests from the response
    counting_requests = response.json()

    # Allow the user to select a counting request to update or delete
    request_name = st.selectbox('Выберите камеру для управления', [req['name'] for req in counting_requests])
    request_id = next((req['request_id'] for req in counting_requests if
                    (req['name'] == request_name)), None)
else:
    request_id = st.sidebar.number_input("Request ID", min_value=1, step=1)

if st.sidebar.button("Получить статистику"):
    # Convert dates to ISO format
    start_period_iso = start_period.strftime("%Y-%m-%dT%H:%M:%S")
    end_period_iso = end_period.strftime("%Y-%m-%dT%H:%M:%S")

    # Fetch aggregated results from the API
    response = requests.get(
        f"{API_URL}/aggregate/",
        params={
            "start_period": start_period_iso,
            "end_period": end_period_iso,
            "step": step,
            "request_id": request_id
        }
    )

    if response.status_code == 200:
        data = response.json()["aggregated_results"]

        # Fetch product and request names
        products_response = requests.get(f"{API_URL}/bread/")
        products = products_response.json()["breads"]
        products_dict = {product["product_id"]: product["name"] for product in products}

        requests_response = requests.get(f"{API_URL}/count/")
        requests_data = requests_response.json()
        requests_dict = {req["request_id"]: req["name"] for req in requests_data}

        # Map IDs to names
        for record in data:
            product_id = record["product_id"]
            if product_id == "Conveyor Idle":
                record["product_name"] = "пустой"
            else:
                record["product_name"] = products_dict.get(product_id, "Неизвестный продукт")

            record["request_name"] = requests_dict.get(request_id, "Неизвестный запрос")

        # Convert to DataFrame for better display
        df = pd.DataFrame(data)

        # Display the results
        st.write("### Статистика")
        st.dataframe(df)
    else:
        st.error("Не получены данные")