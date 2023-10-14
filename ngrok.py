import requests
import json

ngrok_auth_token = ''

def start_ngrok_tunnel(port, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}
    ngrok_api_url = 'https://api.ngrok.com/api/1/tunnels'

    data = {
        'name': 'my_tunnel',
        'addr': "port"
    }

    response = requests.post(ngrok_api_url, headers=headers, data=json.dumps(data))
    if response.status_code == 201:
        return response.json()
    else:
        print(f"Failed to create Ngrok tunnel. Status code: {response.status_code}")
        return None


def get_public_url(ngrok_tunnel_data):
    if ngrok_tunnel_data:
        return ngrok_tunnel_data.get('public_url')
    else:
        return None

if __name__ == '__main__':
    ngrok_tunnel_data = start_ngrok_tunnel(9090, ngrok_auth_token)
    public_url = get_public_url(ngrok_tunnel_data)

    if public_url:
        print(f'Public Ngrok URL: {public_url}')
    else:
        print('Failed to generate Ngrok URL')
