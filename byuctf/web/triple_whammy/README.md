## Triple Whammy

Web challenge with XSS and insecure python deserialization.

After an initial read-through, it seems that there is a bot we have to send to some
location, which indicates some kind of XSS vulnerability. The bot has a cookie set with a secret, with which it is authorized to access certain parts of the web-server that we are not authorized to.


```js Relevant part of the bot's visitUrl 
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