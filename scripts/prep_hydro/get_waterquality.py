
import urllib.request
urllib.request.urlretrieve("http://www.example.com/songs/mp3.mp3", "mp3.mp3")

#---------------
import requests
# Define the base URL
# base_url = "http://datahub.chesapeakebay.net/api.json/WaterQuality/"

base_url = 'http://datahub.chesapeakebay.net/api.csv'

# Example endpoint for programs
endpoint = "Programs"

# Make the request
response = requests.get(f"{base_url}{endpoint}")

# Check the response status
if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"Failed to retrieve data: {response.status_code}")