import uuid
import webbrowser
import socket
import requests

CLIENT_ID = "exilence"
REDIRECT_URI = "https://next.exilence.app/api/authentication/redirect"
SCOPE = "account:stashes account:profile account:characters"
STATE = uuid.uuid4()
AUTH_URL = f"https://www.pathofexile.com/oauth/authorize?client_id={CLIENT_ID}&response_type=code&scope={SCOPE}&state={STATE}&redirect_uri={REDIRECT_URI}"

def send_callback_to_main_instance(callback):
    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the server's address and port
    server_address = ('localhost', 10000)
    client_socket.connect(server_address)

    try:
        # Format the arguments as a string and send them to the server
        arguments = f"{callback}".encode()
        client_socket.sendall(arguments)
    finally:
        # Clean up the connection
        client_socket.close()

def extract_code_and_state(url):
    try:
        if url.startswith("exilence:///?"):
            params_str = url[len("exilence:///?"):]
            params = params_str.split("&")
            code = None
            state = None

            for param in params:
                key, value = param.split("=")
                if key == "code":
                    code = value
                elif key == "state":
                    state = value

            return code.strip(), state.strip()
        else:
            print("Invalid URL format.")
            return None, None
    except Exception as e:
        print("Error while extracting code and state:", e)
        return None, None

def get_oauth_user_validation():
    webbrowser.open(AUTH_URL, new=2)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10000)
    server_socket.bind(server_address)
    server_socket.listen(1)
    while True:
        print("Waiting for a connection...")
        connection, client_address = server_socket.accept()
        try:
            print("Connection established:", client_address)

            data = connection.recv(1024).decode()
            if data:
                print("Received data:", data)
                break

        finally:
            connection.close()

    return extract_code_and_state(data)

def get_new_token(code):
    token_url = f"https://next.exilence.app/api/authentication/oauth2?code={code}"
    print("Calling", token_url)
    response = requests.get(token_url)
    if response.status_code != 200:
        print("Failed to retrieve token: ", response.text)
    print("Got the token : ", response.json())
    return response.json()

def oauth_process():
    print("Starting OAuth2 process...")
    code, state = get_oauth_user_validation()
    print("Got code :", code)
    print("Got state :", state)
    return get_new_token(code)
    