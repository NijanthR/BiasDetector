import requests

url = "http://localhost:8000/api/datasets/upload/"
files = {'file': open(r"C:\Users\srini\Downloads\multi_agent_dataset_testing.csv", 'rb')}
data = {'name': 'multi_agent_dataset_testing'}

try:
    response = requests.post(url, files=files, data=data)
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)
except Exception as e:
    print("Request failed:", str(e))
