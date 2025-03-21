# Client-side python app for SyncUp - testing purposes only. 
# 
# Authors:
#   Kidus Chernet 
#   Ana Ramirez
#   (Extended for Spotify testing)

# Use some code from: Professor Joseph Hummel. 
#

import requests
import json
import uuid
import pathlib
import logging
import sys
import os
import base64
import time
import webbrowser
from urllib.parse import urlparse, parse_qs

from configparser import ConfigParser


############################################################
#
# classes
#
class User:
    def __init__(self, row):
        self.userid = row[0]
        self.username = row[1]
        self.pwdhash = row[2]


class Job:
    def __init__(self, row):
        self.jobid = row[0]
        self.userid = row[1]
        self.status = row[2]
        self.originaldatafile = row[3]
        self.datafilekey = row[4]
        self.resultsfilekey = row[5]


#
# Client-side python app for SyncUp - testing purposes only. 
# 
#
# Authors:
#   Kidus Chernet 
#   Ana Ramirez

# Use some code from: Professor Joseph Hummel. 
#

import requests
import jsons

import uuid
import pathlib
import logging
import sys
import os
import base64
import time

from configparser import ConfigParser

############################################################
#
# classes
#
class User:

  def init(self, row):
    self.userid = row[0]
    self.username = row[1]
    self.pwdhash = row[2]

class Job:

  def init(self, row):
    self.jobid = row[0]
    self.userid = row[1]
    self.status = row[2]
    self.originaldatafile = row[3]
    self.datafilekey = row[4]
    self.resultsfilekey = row[5]

###################################################################
#
# web_service_get
#
# When calling servers on a network, calls can randomly fail. 
# The better approach is to repeat at least N times (typically 
# N=3), and then give up after N tries.
#
def web_service_get(url):
  """
  Submits a GET request to a web service at most 3 times, since 
  web services can fail to respond e.g. to heavy user or internet 
  traffic. If the web service responds with status code 200, 400 
  or 500, we consider this a valid response and return the response.
  Otherwise we try again, at most 3 times. After 3 attempts the 
  function returns with the last response.

  Parameters
  ----------
  url: url for calling the web service

  Returns
  -------
  response received from web service
  """

  try:
    retries = 0

    while True:
      response = requests.get(url)

      if response.status_code in [200, 400, 480, 481, 482, 500]:
        #
        # we consider this a successful call and response
        #
        break;

      #
      # failed, try again?
      #
      retries = retries + 1
      if retries < 3:
        # try at most 3 times
        time.sleep(retries)
        continue

      #
      # if get here, we tried 3 times, we give up:
      #
      break

    return response

  except Exception as e:
    print("ERROR")
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

  Parameters
  ----------
  None

  Returns
  -------
  Command number entered by user (0, 1, 2, ...)
  """
  try:
    print()
    print(">> Enter a command:")
    print("   0 => end")
    print("   1 => register")
    print("   2 => login")
    print("   3 => logout")

    cmd = input()

    if cmd == "":
      cmd = -1
    elif not cmd.isnumeric():
      cmd = -1
    else:
      cmd = int(cmd)

    return cmd

  except Exception as e:
    print("ERROR")
    print("ERROR: invalid input")
    print("**ERROR**")
    logging.error("prompt() failed:")
    logging.error(e)
    return -1
###################################################################
#
# web_service_get
#
# When calling servers on a network, calls can randomly fail. 
# The better approach is to repeat at least N times (typically 
# N=3), and then give up after N tries.
#
def web_service_get(url):
    """
    Submits a GET request to a web service at most 3 times, since 
    web services can fail to respond e.g. to heavy user or internet 
    traffic. If the web service responds with status code 200, 400 
    or 500, we consider this a valid response and return the response.
    Otherwise we try again, at most 3 times. After 3 attempts the 
    function returns with the last response.
    
    Parameters
    ----------
    url: url for calling the web service
    
    Returns
    -------
    response received from web service
    """

    try:
        retries = 0
        
        while True:
            response = requests.get(url)
                
            if response.status_code in [200, 400, 480, 481, 482, 500]:
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
# check_url
#
def check_url(baseurl):
    """
    Performs some checks on the given url, which is read from a config file.
    Returns updated url if it needs to be modified.

    Parameters
    ----------
    baseurl: url for a web service

    Returns
    -------
    same url or an updated version if it contains an error
    """

    # make sure baseurl does not end with /, if so remove:
    if len(baseurl) < 8:
        print("**ERROR: baseurl '", baseurl, "' is not nearly long enough...")
        return None

    if not (baseurl.startswith("http://") or baseurl.startswith("https://")):
        print("**ERROR: baseurl must start with http:// or https://")
        return None

    lastchar = baseurl[len(baseurl) - 1]
    if lastchar == "/":
        baseurl = baseurl[:-1]
        
    return baseurl


############################################################
#
# init
#
def init():
    """
    Initialization function that sets up logging and reads config file

    Parameters
    ----------
    None

    Returns
    -------
    Tuple containing (baseurl, current_user)
    where baseurl is the URL for the web service
    and current_user is None (no user logged in)
    """
    
    # configure logging:
    logging.basicConfig(
        filename='client.log',
        level=logging.WARNING,
        format='%(asctime)s-%(levelname)s-%(message)s',
        datefmt='%Y-%m-%d-%H-%M-%S'
    )

    # logging.debug("debug message")
    # logging.info("info message")
    # logging.warning("warning message")
    # logging.error("error message")
    # logging.critical("critical message")

    # get baseurl from config file:
    configFile = 'syncUP-client.ini'
    
    if not pathlib.Path(configFile).is_file():
        print("**ERROR: config file 'client.ini' does not exist, create and try again")
        return (None, None)
        
    try:
        configur = ConfigParser()
        configur.read(configFile)
    except Exception as e:
        print("**ERROR: unable to read config file")
        logging.error("init() failed:")
        logging.error(e)
        return (None, None)
        
    baseurl = configur.get('client', 'webservice')
    
    baseurl = check_url(baseurl)
    if baseurl is None:
        return (None, None)
        
    # initialize user to None, meaning no one is logged in
    current_user = None
    
    return (baseurl, current_user)


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
    
    print("Enter password>")
    password = input()
    
    # build web service URL:
    api = '/register'
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
def login(baseurl):
    """
    Prompts user to login by entering their username and 
    password. If successful, a connection to the web server
    is established.

    Parameters
    ----------
    baseurl: baseurl for web service

    Returns
    -------
    user object if successful, None if not
    """

    print("Login to your account...")
    print()

    # get user input:
    print("Enter username>")
    username = input()

    print("Enter password>")
    password = input()

    # build web service URL:
    api = '/login'
    url = baseurl + api

    # add query params:
    params = {'username': username, 'password': password}
    url += '?' + '&'.join([f"{key}={requests.utils.quote(str(value))}" for key, value in params.items()])

    # call web service:
    print("Calling web service...")
    response = web_service_get(url)

    if response is None:
        print("**ERROR: failed to call web service, no response")
        return None

    # analyze response:
    if response.status_code != 200:
        print("**ERROR: web service returned status code", response.status_code)
        try:
            jsonResponse = response.json()
            print(json.dumps(jsonResponse, indent=2))
        except:
            print("Response:", response.text)
        return None

    try:
        jsonResponse = response.json()
    except Exception as e:
        print("**ERROR: unable to parse response as JSON")
        print("Response:", response.text)
        logging.error("login() failed:")
        logging.error(e)
        return None

    # display results:
    if "userid" not in jsonResponse:
        print("**ERROR: unexpected response, no userid returned")
        print("Response:", jsonResponse)
        return None

    # create user object to return:
    try:
        user = User([jsonResponse["userid"], username, ""])
    except Exception as e:
        print("**ERROR: unable to create User object from response")
        print("Response:", jsonResponse)
        logging.error("login() failed:")
        logging.error(e)
        return None

    print("Login successful, userid:", user.userid)
    return user


############################################################
#
# logout
#
def logout(current_user):
    """
    Logout => server-side this would be terminating the 
    session, but in this case we just set the current_user
    to None so no user is logged in.

    Parameters
    ----------
    current_user: user object representing the current user

    Returns
    -------
    None to indicate no one is logged in
    """

    if current_user is None:
        print("No user is currently logged in...")
        return None

    #
    # These would be additional actions to take if we
    # were using sessions server-side, but we're not so
    # we just return None so no one is logged in:
    #
    current_user = None
    print("You have been logged out.")
    return current_user


############################################################
#
# test_callback
#
def test_callback(baseurl):
    """
    Manually test the callback by providing the code and state from 
    the browser redirect URL
    
    Parameters
    ----------
    baseurl: baseurl for web service
    
    Returns
    -------
    None
    """
    
    print("Test callback manually...")
    print()
    
    print("Enter the authorization code from the browser redirect (code parameter)>")
    code = input()
    
    print("Enter the state parameter from the browser redirect>")
    state = input()
    
    # build web service URL:
    api = '/callback'
    url = baseurl + api
    
    # add query params:
    params = {'code': code, 'state': state}
    url += '?' + '&'.join([f"{key}={requests.utils.quote(str(value))}" for key, value in params.items()])
    
    # call web service:
    print("Calling callback web service...")
    response = web_service_get(url)
    
    if response is None:
        print("**ERROR: failed to call web service, no response")
        return
        
    # analyze response:
    print(f"Response status code: {response.status_code}")
    
    if response.status_code == 302:
        redirect_url = response.headers.get('Location')
        print(f"Received redirect to: {redirect_url}")
        
        # Parse the redirect URL to show parameters
        parsed_url = urlparse(redirect_url)
        query_params = parse_qs(parsed_url.query)
        print("\nRedirect parameters:")
        for key, value in query_params.items():
            print(f"  {key}: {value[0]}")
            
        print("\nOpening browser to see the final result...")
        webbrowser.open(redirect_url)
    else:
        try:
            jsonResponse = response.json()
            print("Web service returned:")
            print(json.dumps(jsonResponse, indent=2))
        except:
            print("Response text:", response.text)


############################################################
#
# main
#
print('** Welcome to SyncUp Testing Client **')
print()

# initialize:
baseurl, current_user = init()
if baseurl is None:
    print("**ERROR: Failed to initialize, exiting")
    sys.exit(0)

print("Web service URL:", baseurl)
print()

# main loop:
cmd = prompt()

while cmd != 0:
    #
    # register
    #
    if cmd == 1:
        register(baseurl)
    #
    # login
    #
    elif cmd == 2:
        user = login(baseurl)
        if user is not None:  # success
            current_user = user
    #
    # logout
    #
    elif cmd == 3:
        current_user = logout(current_user)
    #
    # test callback manually
    #
    elif cmd == 4:
        test_callback(baseurl)
    #
    # unknown command
    #
    else:
        print("** Unknown command, try again...")
    
    # prompt for next command:
    if current_user is None:
        cmd = prompt()
    else:
        print()
        print(">> You are logged in as", current_user.username)
        cmd = prompt()

# done
print()
print('** Done **')