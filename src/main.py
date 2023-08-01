from auth import oauth, token
import systray
import sys

systrayHandler = None

def main():
    systrayHandler = systray.run_systray()
    newToken = token.get_token()
    print(newToken)
    sys.exit()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("Starting the tool")
        main()
    else:
        print("We are the second instance, passing the arguments to the main one :")
        print(sys.argv[1])
        oauth.send_callback_to_main_instance(sys.argv[1])
        sys.exit()




# @app.route("/")
# def index():
#     return redirect(AUTH_URL)

# @app.route("/callback")
# def callback():
#     code = request.args.get("code")
#     if not code:
#         return "Authorization code not received."

#     # Exchange the authorization code for access_token and refresh_token
#     token_url = "https://www.pathofexile.com/oauth/token"
#     data = {
#         "grant_type": "authorization_code",
#         "code": code,
#         "client_id": CLIENT_ID,
#         "client_secret": CLIENT_SECRET,
#         "redirect_uri": REDIRECT_URI
#     }

#     response = requests.post(token_url, data=data)
#     if response.status_code != 200:
#         return f"Failed to retrieve tokens: {response.text}"

#     tokens = response.json()
#     access_token = tokens["access_token"]

#     # Use the access_token to make a request to the API
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "User-Agent": "<product> / <product-version> <comment>"
#     }

#     response = requests.get(API_BASE_URL, headers=headers)
#     if response.status_code != 200:
#         return f"Failed to fetch data from the API: {response.text}"

#     user_data = response.json()
#     # Now you have the user data from the API
#     # You can parse and use it as per your requirement

#     return f"User data: {user_data}"