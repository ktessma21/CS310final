#
# Client-side python app for Social Media App, which is calling
# a set of lambda functions in AWS through API Gateway.
# The overall purpose of the app is to manage a simple social network
# where users can follow each other and view followers.
#
# Authors:
#  Ana Ramirez
#

import requests
import json
import pathlib
import logging
import sys
import os
import time
import getpass

from configparser import ConfigParser


############################################################
#
# Classes
#
class User:
  def __init__(self, row):
    self.userid = row[0]
    self.username = row[1]

class Follower:
  def __init__(self, data):
    self.userid = data['userid']
    self.username = data['username']


###################################################################
#
# web_service_get
#
def web_service_get(url, headers=None):
  """
  Submits a GET request to a web service with retries
  
  Parameters
  ----------
  url: url for calling the web service
  headers: optional headers to include
  
  Returns
  -------
  response received from web service
  """
  try:
    retries = 0
    
    while True:
      if headers:
        response = requests.get(url, headers=headers)
      else:
        response = requests.get(url)
        
      if response.status_code in [200, 400, 401, 404, 409, 500]:
        # we consider this a successful call and response
        break

      # failed, try again?
      retries = retries + 1
      if retries < 3:
        # try at most 3 times
        time.sleep(retries)
        continue
          
      # if get here, we tried 3 times, we give up:
      break

    return response

  except Exception as e:
    print("**ERROR**")
    logging.error("web_service_get() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return None
    

############################################################
#
# prompt
#
def prompt():
  """
  Prompts the user and returns the command number
  """
  try:
    print()
    print(">> Enter a command:")
    print("   0 => end")
    print("   1 => users")
    print("   2 => login")
    print("   3 => show followers")
    print("   4 => follow user")
    print("   5 => logout")

    cmd = input()

    if cmd == "":
      cmd = -1
    elif not cmd.isnumeric():
      cmd = -1
    else:
      cmd = int(cmd)

    return cmd

  except Exception as e:
    print("**ERROR")
    print("**ERROR: invalid input")
    print("**ERROR")
    return -1


############################################################
#
# users
#
def users(baseurl):
  """
  Prints out all the users in the database
  """
  try:
    # call the web service:
    api = '/users'
    url = baseurl + api

    res = web_service_get(url)

    # let's look at what we got back:
    if res.status_code == 200: # success
      pass
    else:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 500:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      return

    # deserialize and extract users:
    body = res.json()

    # map each row into a User object:
    users = []
    for row in body:
      user = User(row)
      users.append(user)
    
    if len(users) == 0:
      print("No users found...")
      return

    print("\nUsers:")
    print("-" * 30)
    for user in users:
      print(f"User ID: {user.userid}")
      print(f"Username: {user.username}")
      print("-" * 30)
    
    return

  except Exception as e:
    logging.error("**ERROR: users() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


############################################################
#
# show_followers
#
def show_followers(baseurl, token):
  """
  Shows followers for the current authenticated user
  """
  try:
    if not token:
      print("No current token, please log in")
      return
      
    print("Retrieving your followers...")
    
    # Call the web service - we don't need to send a user ID
    # since the server will get it from the token
    api = '/followers'
    url = baseurl + api
    
    headers = {"Authentication": token}
    
    res = web_service_get(url, headers)
    
    # Process response
    if res.status_code == 200:  # success
      body = res.json()
      followers = body['followers']
      count = body['follower_count']
      
      print(f"\nYour Followers ({count}):")
      print("-" * 30)
      
      if count == 0:
        print("You don't have any followers yet.")
      else:
        for follower in followers:
          print(f"User ID: {follower['userid']}")
          print(f"Username: {follower['username']}")
          print("-" * 30)
          
    elif res.status_code == 401:
      print("Authentication failed. Please log in again.")
    else:
      # failed
      print(f"Failed with status code: {res.status_code}")
      print(f"URL: {url}")
      
      if res.status_code in [400, 500]:
        # we'll have an error message
        body = res.json()
        print(f"Error message: {body}")
      
    return

  except Exception as e:
    logging.error("**ERROR: show_followers() failed:")
    logging.error(f"url: {url}")
    logging.error(e)
    return

  except Exception as e:
    logging.error("**ERROR: show_followers() failed:")
    logging.error(f"url: {url}")
    logging.error(e)
    return


############################################################
#
# register
#
def register(baseurl):
    """
    Registers a new user 
    
    Parameters
    ----------
    baseurl: baseurl for web service
    
    Returns
    -------
    None
    """
    
    print("Registering a new user...")
    print()
    
    # get user input:
    print("Enter firstname>")
    firstname = input()
    
    print("Enter lastname (optional)>")
    lastname = input()
    
    print("Enter username>")
    username = input()
    
    if not username.strip():
      print("Username cannot be empty.")
      return
    
    # Prepare data for request
    data = {
      "username": username
    }
    
    # Call the web service
    api = '/unfollow'
    url = baseurl + api
    
    # add query params:
    data = {'firstname': firstname, 'username': username, 'password': password}
    if lastname.strip() != "":
        data['lastname'] = lastname

    print("calling web service...")
    response = requests.post(url, json=data)
    
    if response is None:
        print("**ERROR: failed to call web service, no response")
        return
        
    # analyze response:
    if response.status_code != 200 and response.status_code != 302:
        print("**ERROR: web service returned status code", response.status_code)
        try:
            jsonResponse = response.json()
            print(json.dumps(jsonResponse, indent=2))
        except:
            print("Response:", response.text)
        return
    
    try:
        # The response could be a redirect or JSON
        if response.status_code == 302:
            # Handle redirect response
            redirect_url = response.headers.get('Location')
            print(response.text)
            print(f"Received redirect to: {redirect_url}")
            print("Opening browser for Spotify authorization...")
            webbrowser.open(redirect_url)
            print("\nAfter authorizing in the browser, the system will redirect to your callback URL.")
            print("You'll need to manually check your server logs for the callback processing.")
            return
        else:
            # Handle JSON response
            jsonResponse = response.json()
            print("Web service returned:")
            print(json.dumps(jsonResponse, indent=2))
            
            # Check if response contains a Spotify auth URL to open
            if "spotify_auth_url" in jsonResponse:
                print("\nOpening browser for Spotify authorization...")
                webbrowser.open(jsonResponse["spotify_auth_url"])
                print("\nAfter authorizing in the browser, the system will redirect to your callback URL.")
                print("Registration token:", jsonResponse.get("registration_token", "Not provided"))
                
                # Wait for manual confirmation from user
                print("\nPress Enter after you've completed the Spotify authorization process...")
                input()
                
            
    except Exception as e:
        print("**ERROR: unable to parse response as JSON")
        print("Response:", response.text)
        logging.error("register() failed:")
        logging.error(e)
        return

############################################################
#
# login
#
    

def login(auth_url):
  """
  Prompts the user for a username and password, then tries
  to log them in. If successful, returns the token returned
  by the authentication service.
  """
  try:
    username = input("username: ")
    password = getpass.getpass()
    duration = input("# of minutes before expiration? [ENTER for default] ")

    # build message:
    if duration == "":  # use default
      data = {"username": username, "password": password}
    else:
      data = {"username": username, "password": password, "duration": duration}

    # call the auth web service:
    api = '/auth'
    url = auth_url + api

    res = requests.post(url, json=data)

    # clear password variable:
    password = None

    # process the response:
    if res.status_code == 401:
      # authentication failed:
      body = res.json()
      print(body)
      return None

    if res.status_code == 200: # success
      pass
    elif res.status_code in [400, 500]:
      # we'll have an error message
      body = res.json()
      print("**Error:", body)
      return None
    else:
      # failed:
      print("**ERROR: Failed with status code:", res.status_code)
      print("url: " + url)
      return None

    # success, extract token:
    body = res.json()
    token = body
    print("Logged in successfully, token:", token)
    return token

  except Exception as e:
    logging.error("**ERROR: login() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return None


############################################################
#
# check_url
#
def check_url(baseurl):
  """
  Validates and formats the URL from config
  """
  if len(baseurl) < 16:
    print("**ERROR: baseurl '", baseurl, "' is not nearly long enough...")
    sys.exit(0)

  if baseurl == "https://YOUR_GATEWAY_API.amazonaws.com":
    print("**ERROR: update config file with your gateway endpoint")
    sys.exit(0)

  if baseurl.startswith("http:"):
    print("**ERROR: your URL starts with 'http', it should start with 'https'")
    sys.exit(0)

  lastchar = baseurl[len(baseurl) - 1]
  if lastchar == "/":
    baseurl = baseurl[:-1]
    
  return baseurl


############################################################
# main
#
try:
  print('** Welcome to Social Media App **')
  print()



  #
  # we have two config files:
  # 
  #    1. socialapp API endpoint
  #    2. authentication service API endpoint
  #
  #
  socialapp_config_file = 'syncUP-client.ini'
  authsvc_config_file = 'auth-config.ini'

  print("First, enter name of SocialApp config file to use...")
  print("Press ENTER to use default, or")
  print("enter config file name>")
  s = input()

  if s == "":  # use default
    pass  # already set
  else:
    socialapp_config_file = s

  # does config file exist?
  if not pathlib.Path(socialapp_config_file).is_file():
    print("**ERROR: socialapp config file '", socialapp_config_file, "' does not exist, exiting")
    sys.exit(0)

  # setup base URL to web service:
  configur = ConfigParser()
  configur.read(socialapp_config_file)
  baseurl = configur.get('client', 'webservice')
  
  baseurl = check_url(baseurl)
  
  # now we need to process the 2nd config file:
  print("Second, enter name of Auth Service config file to use...")
  print("Press ENTER to use default, or")
  print("enter config file name>")
  s = input()

  if s == "":  # use default
    pass  # already set
  else:
    authsvc_config_file = s

  # does config file exist?
  if not pathlib.Path(authsvc_config_file).is_file():
    print("**ERROR: authsvc config file '", authsvc_config_file, "' does not exist, exiting")
    sys.exit(0)

  # setup base URL to auth service:
  configur.read(authsvc_config_file)
  auth_url = configur.get('client', 'webservice')
  
  auth_url = check_url(auth_url)

  # initialize login token:
  token = None

  # main processing loop:
  cmd = prompt()

  while cmd != 0:
    if cmd == 1:
      users(baseurl)
    elif cmd == 2:
      token = login(auth_url)
    elif cmd == 3:
      show_followers(baseurl, token)
    elif cmd == 4:
      follow_user(baseurl, token)
    elif cmd == 5:
      # logout
      token = None
      print("Logged out successfully")
    else:
      print("** Unknown command, try again...")
    
    cmd = prompt()

  # done
  print()
  print('** done **')
  sys.exit(0)

except Exception as e:
  logging.error("**ERROR: main() failed:")
  logging.error(e)
  sys.exit(0)
