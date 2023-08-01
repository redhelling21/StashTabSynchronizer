import uuid
import webbrowser
import socket
import requests
from confighandler import config as cfg
from logger import appLogger, subLogger

conf = cfg.loadConfig()["oauth"]
STATE = uuid.uuid4()
SCOPE = conf["scope"]
REDIRECT_URI = conf["redirect"]
CLIENT_ID = conf["clientId"]
AUTH_TEMPLATE = conf["authTemplate"]
TOKEN_TEMPLATE = conf["tokenTemplate"]

def send_callback_to_main_instance(callback):
    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the server's address and port
    server_address = ('localhost', 10000)
    subLogger.debug("Connecting to socket %s", str(server_address))
    client_socket.connect(server_address)
    
    try:
        # Format the arguments as a string and send them to the server
        arguments = f"{callback}".encode()
        client_socket.sendall(arguments)
        subLogger.info("Sent the callback to the main instance")
    except Exception as e:
        subLogger.exception("An exception occurred when passing the callback to the main instance : %s", str(e))
    finally:
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
            appLogger.info("Extracted code : %s and state : %s", code, state)
            return code, state
        else:
            appLogger.error("%s does not start with exilence:///?", url)
            return None, None
    except Exception as e:
        appLogger.exception("An exception occurred while extracting code and state: %s", str(e))
        return None, None

def get_oauth_user_validation():
    appLogger.info("Getting the user approval")
    authUrl = AUTH_TEMPLATE.format(CLIENT_ID=CLIENT_ID, SCOPE=SCOPE, STATE=STATE, REDIRECT_URI=REDIRECT_URI)
    appLogger.debug("Opening %s", authUrl)
    webbrowser.open(authUrl, new=2)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 10000)
    server_socket.bind(server_address)
    server_socket.listen(1)
    while True:
        appLogger.info("Waiting for OAuth server callback")
        connection, client_address = server_socket.accept()
        try:
            appLogger.debug("Socket connection established :%s", client_address)
            data = connection.recv(1024).decode()
            if data:
                appLogger.info("Received callback : %s", str(data))
                break

        finally:
            connection.close()

    return extract_code_and_state(data)

def get_new_token(code):
    appLogger.info("Asking the remote server for a token")
    tokenUrl = TOKEN_TEMPLATE.format(CODE=code)
    appLogger.debug("Calling %s", tokenUrl)
    response = requests.get(tokenUrl)
    if response.status_code != 200:
        appLogger.error("Failed to retrieve token: %s", response.text)
    appLogger.info("Acquired the token %s", str(response.json()))
    return response.json()

def oauth_process():
    appLogger.info("Starting the OAuth2 process")
    code, state = get_oauth_user_validation()
    return get_new_token(code)
    