## Calculator

Calculator was a relatively simple web challenge that abused the fact that passing JSON between python and javascript might not always
do what we expect.

To keep it short, the expression_parser.ts will parse our input into a JSON object and pass it to the python code. This will evaluate it
and return the result in a JSON object back to the javascript code. If this JSON object we get back from python looks like a JSON object but
fails to parse as JSON in javascript, we get the flag.

```js
function * parseFloat (string: string): ParseResult {
  for (const regex of [
    /[-+](?:\d+\.?|\d*\.\d+)(?:e[-+]?\d+)?$/,
    /(?:\d+\.?|\d*\.\d+)(?:e[-+]?\d+)?$/
  ]) {
    const match = string.match(regex)
    if (!match) {
      continue
    }
    const number = +match[0]
    if (Number.isFinite(number)) {
      yield {
        expr: { value: number },
        string: string.slice(0, -match[0].length)
      }
    }
  }
}
```

This function is what gave me the following idea: Is there a difference in what javascript and python think is a "finite" number? I started
thinking about `NAN` and built a PoC that showed, that if we got the python code to evaluate the calculation to `NAN`, we would get the flag.

### Hunting NAN (Not the bread.)

I tried to divide by `0`. However, dividing by `0` will throw an exception in python, so that's no good. Looking through
the documentation of python math-operations and all the ways we can generate `NAN`, I came across another interesting value: `Inf`. I tried that in 
my PoC and it also showed to give us the flag. However, simply giving a very big number turned out to not solve the challenge. This was because
the above code snippet already would prevent too big numbers to even reach the python code.

The solution was to multiply two very big numbers with each others. The python code returns `Inf`, which the JS code does not understand and instead
gives us the flag as compensation. Thanks JS code!