import requests
from flask import Flask, render_template,request

"""
Idea when a virus is found the smartermail server will send a notification to the user the user will then be able to click the link and enter the eml name then have it resent to the user. 

"""

def auth(username, password):
    authurl = url + "/api/v1/auth/authenticate-user"
    myobj = {'username': username, 'password':password}
   # print("test")
    data = requests.post(authurl, data = myobj) # this posts the username and password to the api
    #print("test")
   # print(data.json())
    refreshToken = data.json()['refreshToken'] # this is the refresh token
    accessToken = data.json()['accessToken'] # this is the access token
    accessTokenExpiration = data.json()['accessTokenExpiration'] # this is the access token expiration date
    access_info = {'accessToken': accessToken, 'accessTokenExpiration': accessTokenExpiration, 'refreshToken': refreshToken} # this is the access token, refresh token and expiration info
    auth = access_info['accessToken'] # this is the access token """
    return auth

def resendfromquarantine(eml,path,auth_token):
    global url
    authurl = url + "/api/v1/settings/sysadmin/resend-quarantine-messages"
    myobj = {"spoolInput":[{"fileName":eml,"spoolName":path}]}
    print(auth_token)
    headers = {'Authorization': 'Bearer ' + auth_token}
    r = requests.post(authurl, headers=headers,json = myobj)
    return r.json()

def spoolmessages(auth,eml):
    global url
    authurl = url + '/api/v1/settings/sysadmin/spool-messages'
    headers = {'Authorization': 'Bearer ' + auth}
    body =  {"spoolInput":[{"startIndex":0,"count":"200","sortType":"2","search":"","ascending":True,"filter":"quarantine_virus"}]}
    r = requests.post(authurl, headers=headers,json = body)
    r = r.json()
    for i in r['spoolListData']:
        for j in i['messages']:
            if j['fileName'] == eml:
                s = j['spoolName']
                return s
    #loop 100 times
    for i in range(100):
        body =  {"spoolInput":[{"startIndex":i,"count":"200","sortType":"2","search":"","ascending":True,"filter":"quarantine_virus"}]}
        r = requests.post(authurl, headers=headers,json = body)
        r = r.json()
        for i in r['spoolListData']:
            for j in i['messages']:
                if j['fileName'] == eml:
                    s = j['spoolName']
                    return s
    return "not found"


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/resend', methods=['POST'])
def resend():
    global auth_c
    global username
    global password
    auth_c = auth(username, password)
    #get information from form
    eml = request.form['eml']
    print(eml)
    x = spoolmessages(auth_c,eml)
    if x == "not found":
        return "not found"
    x = resendfromquarantine(eml,x,auth_c)
    if x['success'] == True:
        return "success"
    else:
        return "failed"




username = ''
password = ''
url = ''
with open('creds.txt') as f:
    for line in f:
        if line.startswith('url'):
            url = line.split('=')[1]
        elif line.startswith('username'):
            username = line.split('=')[1]
        elif line.startswith('password'):
            password = line.split('=')[1]
        elif line.startswith('port'):
            port = line.split('=')[1]
    #remove newline character from pushbullet_access
    url = url.rstrip('\n')
    username = username.rstrip('\n')
    password = password.rstrip('\n')
    port = port.rstrip('\n')
    print(url)
    print(username)
    print(password)
    auth_c = auth(username, password)


#{"spoolInput":[{"fileName":"11626010.eml","spoolName":"c:\\SmarterMail\\Spool\\Quarantine\\2022-09-01"}]}







#run app
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=port) 