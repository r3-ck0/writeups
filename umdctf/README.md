# Info

This was a very fun CTF I played with the World Wide Flags team. We came in 9th. Thanks to n0s for the sleepless night solving 
stupid Erlang challenges!

## Writeups

### Web

#### Donations

This was a very quick and simple web challenge. 
Simply make an account and donate negative money to Jeff Bezos and you get your flag.

#### HTTP Fanatics

This was a whitebox web challenge. 

When accessing the website directly, it tells us to use HTTP3, which I didn't even know existed.
We first ignore that and look at the code for the webserver. Turns out there are actually two webservers
running that seem to interact in some way. The python server looks very vulnerable as we can just simply
register a user and read the dashboard, which we assume hosts the flag:

```
@app.post("/admin/register")
def register(user: Registration):
    print(user)
    if not re.match(r"[a-zA-Z]{1,8}", user.username):
        return Response(status_code=400, content="Bad Request")

    users[user.username] = user.password
    return Response(status_code=204)


@app.get("/dashboard")
def dashboard(credentials: Annotated[str | None, Cookie()] = None):
    if not credentials:
        return Response(status_code=401, content="Unauthorized")

    user_info = json.loads(base64.b64decode(credentials))

    if user_info["username"] not in users or user_info["password"] != users[user_info["username"]]:
        return Response(status_code=401, content="Unauthorized")

    with open("static/dashboard.html") as dashboard_file:
        return HTMLResponse(content=dashboard_file.read())
```

So we spin up the python webserver, put some breakpoints and are quickly able to access the dashboard.

The tricky part is, that there is a rust webserver also running. So whenever we send a request to the webserver,
it seems to be redirected to the rust webserver.

The quickest way I found to send HTTP3 requests was to use a new `cURL` version that supports --http3-only.
When trying this, our exploit that only ran on the python server is not working.

After some fiddling around, we find that sending the request using `--http1.1` redirects the request directly to
the python server. So it was just a matter of running the same exploit using `--http1.1` instead.

#### UMDProxy

This was a blackbox web challenge.

The attack surface was a website that, presented itself as supplying proxies to the world. However, when registering, they asked
us to give them access to our proxy so they can rent it out and promise to give us credits for a flag in return.
The website provides a field where we can put the hostname of a proxy and it will try to connect to it. If it is successful, we get 2k credits.
We need 10k credits in total to win the flag.

We set up a proxy on a vServer and see what this request actually does. It turns out that it tries 5 times to CONNECT through the proxy to
itself. When it's successful, we get 2k credits. Because of the `5 times` and the `2k credits`, we get a hunch that it might have something
to do with a race condition. We go through some free proxies available on the internet and sometimes we receive more
than 2k points (4k, 6k, even 8k). We come up with the following idea:

The client sends a CONNECT request. When this request fails, we are sure we don't get 2k.
So we want to fulfill the CONNECT request and, after that, tunnel the uplink data through but refrain from sending all the downlink data down
immediately. This idea is realized in the following crude and sluggish proxy server implementation:

```
import socket
import ssl
import threading
import time


data_to_send = []

def handle_client(client_socket):
    # Receive data from the client
    request = client_socket.recv(4096)
    # Parse the first line of the HTTP request
    first_line = request.split(b'\n')[0]
    method, url, _ = first_line.split(b' ')

    print(request)

    if method == b'CONNECT':
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect(("challs.umdctf.io", 31111))
        print("Received connect request")

        client_socket.send(b'HTTP/1.1 200 OK\r\n\r\n')

        # Pass data between the client and server
        for i in range(3):
            gotData = False

            data = client_socket.recv(4096)
            if data:
                remote_socket.sendall(data)
                print("Upstream: " + str(data))
                gotData = True

            if i == 1:
                time.sleep(2)

            data = remote_socket.recv(4096)
            if data:
                client_socket.sendall(data)
                print("Downstream: " + str(data))
                gotData = True

            if not gotData:
                break



def main():
    # Set up a listening socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 30000))
    server_socket.listen(5)

    print("[*] Listening on 0.0.0.0:30000")

    while True:
        client_socket, addr = server_socket.accept()
        print("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))

        # Start a new thread to handle the client's request
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    main()
```

When running this proxy and giving it to the website and also finetuning the 
delays and amount of data to passthrough without error, we receive 22k credits (?).

### PWN

#### ReadyAimFire

This was an interesting C++ pwn challenge. The overflow is fairly obvious and the main idea
is that the default code path throws an exception. The flag is being output inside another exception handler.

So after doing some research on C++ exceptions, we find out that the choice, which exception handler to call
is made by the address that is in the program counter while the exception is thrown. The exception handling
system then unwinds the stack to find the first exception handler that is responsible. This unwinding is nothing
else than walking up the stack frames and finding the first return address that has an exception handler.

So we need to overflow the stack and write the return address to be in the `try` block of the `try-catch` construct
for which the flag is printed in the `catch` block.

One last thing to put everything together was that we needed to overwrite not the next return address but the one after that.
This meant overwriting some heap addresses. For this we were given a heap pointer, so it was fairly easy to overwrite the
heap addresses with themselves by computing the offsets from the heap leak.

### Rev

#### Flavors

This was an arcane experience. First we needed to find out that we are dealing with an Erlang binary, which turned out to
actually be an Elixir binary that runs in the ErlangVM. We then needed to understand how to run this binary, which
brought us the joys of the Elixir interactive console `iEX`. After finding out how anything works in `iEX`, we were
able to decompile the beam file we were given.

After learning a bit of Erlang, we found a string that we could provide to the main function which made it output only zeros.
Whenever we changed a character in that string, one of the zero bytes turned into a different byte.

The goal of the challenge was to replicate a certain byte string.

We guessed the first few characters `UMDCTF{` and knew, that we were on the right track. Instead of writing a quick python script,
that could have solved it in a few seconds, we decided to manually reconstruct the string, which took us over an hour in the middle
of the night. But it was a very fun experience.