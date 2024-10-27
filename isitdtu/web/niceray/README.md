# Niceray

Niceray was a relatively simple challenge, however I still had trouble at cracking the remote and I finally didn't manage to solve it in time.

We get the code for a java based webserver. The server turns out to be a liferay portal, and after some googling and using searchsploit, we find that
there might be some metasploit exploits to use. Expecting it to be a newer version, I first tried the latest exploit, however it didn't seem to work.

Some more googling provided [this blog post](https://code-white.com/blog/2020-03-liferay-portal-json-vulns/) which looked reasonable, however the blog-post was kind of
confusing and I could not get the PoC to work.

Finally, I fell onto the metasploit module `multi/http/liferay_java_unmarshalling`. This exploit ran locally without issues, however I could until the end not get it to work on the remote server.
My assumption was that it was due to the firewall configurations. Looking at the IPTABLES configuration, inbound traffic is unrestricted, while outbound traffic is restricted to port 53. The exploit itself
needs two connections to work successfully: One to serve the serialized classes - the krux of the exploit, and one to accept a reverse-shell connection. As outbound traffic is restricted to a single port, this
became a bottleneck. I could serve the exploit, could see the server accessing it, however I couldn't get a shell. I tried circumventing it using a bind-shell - usually the inbound traffic is regulated, but in this case it wasn't.
I was confused when this also didn't work. Finally, the last thing I tried was to spin up a VPS. I installed metasploit and ran a meterpreter listener. From the first machine, I sent the exploit including the information on where to get the meterpreter payload. The server would then
connect to the VPS, download the meterpreter stage and run the rev-shell. However, for some reason this did not work as expected and I finally ran out of time.

