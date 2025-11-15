import requests
try:
    response = requests.get('http://localhost:5001')
    print(f'Server response status code: {response.status_code}')
    if response.status_code == 200:
        print('Server is running successfully!')
    else:
        print('Server returned error status code')
except Exception as e:
    print(f'Error connecting to server: {e}')