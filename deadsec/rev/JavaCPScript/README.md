# JavaCPScript

## Introduction 
This was a white-box nodejs challenge which tried to break your brain with a taskscheduler, coded by the intern.
When reading through the code, it quickly became clear that there are indirections over indirections, making it difficult to understand the control flow just by static analysis, however still, that is where we started after an initial first run of the software.

## First Run
On our first run, we see that the code takes a long time to process (10s). Once it's done it tells us `flag: false`, which informs us on what our goal is: `flag: true`. There is an `input` file, that contains `DEAD{redacted}` which we assume is read by the program. So the assumption for the target is: Put the correct flag in the `input` and get told that your `flag` is `true`.

## Static Analysis
### Analysis
One of the more interesting parts of the code is in the `main.js` file. We can see a statement that reads as:

```js
....
    return ProcessTask(3895813, null, 
        (task) => ProcessTask(3893664, task,
        (task) => ProcessTask(3895583, task,
        (task) => ProcessTask(3893639, task,
        (task) => ProcessTask(3919755, task,
        (task) => ProcessTask(3893694, task,
        (task) => ProcessTask(3871506, task,
        (task) => ProcessTask(3871544, task,
        (task) => ProcessTask(3810527, task,
        (task) => ProcessTask(3921672, task,
        (task) => ProcessTask(3913158, task,
        (task) => ProcessTask(3813122, task,
        (task) => ProcessTask(3869603, task,
        (task) => ProcessTask(3813209, task,
        (task) => ProcessTask(3910936, task,
        (task) => ProcessTask(3911023, task,
        (task) => ProcessTask(3896081, task,
        (task) => ProcessTask(3822626, task,
        (task) => ProcessTask(3913160, task,
        (task) => ProcessTask(3919793, task,
        (task) => ProcessTask(3822653, task,
        (task) => ProcessTask(3895614, task,
        (task) => ProcessTask(3820987, task,
        (task) => ProcessTask(3820987, task,
        (task) => ProcessTask(3932159, task,
        (task) => ProcessTask(3911025, task,
        (task) => ProcessTask(3893657, task,
        (task) => ProcessTask(3921671, task,
        (task) => ProcessTask(3820578, task,
        (task) => ProcessTask(3921709, task,
        (task) => ProcessTask(3921698, task,
        (task) => ProcessTask(3910918, task, (task) => Solver(task, action, (flag) => { console.log(`flag: ${flag}`); })
    ))))))))))))))))))))))))))))))));
}
```

Reading through the implementations for ProcessTask, it looks like the integer value at the start is some task id. The last argument is a function that is to be executed by the task. However, it's not simply executed, it's given to a mess of indirections and schedulers and it's called from within a different function providing information on whether or not `flag` is `true`. 
The following piece of code shows when this happens. `c(g)` is the call of the lambda above, where `g` is true or false, whether the flag was correct or not. The flag is thus correct if `e` or `f` are null, which correspond to the `task` and `action` parameters of the `Solver` call. 


### Conclusion
My understanding was thus: If we manage to execute all of the tasks in the process list that we added, trickling down to the one providing `null` as a task, our flag will be `true`.

## Dynamic Analysis
After some initial static analysis, I switched to dynamically analysing the binary. I put breakpoints at rather random locations and single-stepped through to get a feeling of how everything is executed. After doing that for a while, I found that the following code in `main.js` had a peculiar behaviour.

```js
    function taskHandler(taskId, action) {
        if (taskId < 0x900)
            return ProcessTask(taskId, action, (a) => { return execute(taskId + 1, a); })
        else {
            return ProcessTaskSequence(action,
                (id, i, completeTask) => {
                    return TaskManager((r) => {
                        return async (i, obj) => {
                            let idx = (id % 8) ? 0 : 1;
                            switch (i) {
                                case 0:
                                    await callReadFileSync(obj, mutex[idx], id);
                                    break;
                                case 1:
                                    callSetTimeout(obj, mutex[idx]);
                                    callImmediate(obj, mutex[idx]);
                                    break;
                                case 2:
                                    callNextTick(obj);
                                    obj.data ^= ((obj.data >> 6) | (obj.data << 2));
                                    break;
                                default:
                                    return completeTask(obj);
                            }
                            await sleep(0);
                            console.error(obj.data)
                            return r(i + 1,obj);
                        }})(0, { data: id });
                },
                ...
```

It looked like a state machine, going through case 0, then 1, then 2, then to default, all while manipulating `obj.data`. Finally, `obj` is passed to `completeTask`. `completeTask` will start the task with the id that it is given (in our case `obj`). The `id`s would decrement from `2304` (which took me a while to understand, is `0x900`), go through several manipulations before being provided to `completeTask`.

The manipulating functions are:

```js
async function callImmediate(obj, mutex) {
    setImmediate(async (...args) => {
        const [ release ] = args;
        obj.data ^= ((obj.data >> 7) | (obj.data << 1));
        release();
    }, await mutex.lock());
}
    
async function callSetTimeout(obj, mutex) {
    setTimeout(async (...args) => {
        const [release] = args;
        obj.data ^= ((obj.data >> 4) | (obj.data << 4));
        release();
    }, 0, await mutex.lock());
}
    
async function callNextTick(obj) {
    process.nextTick(() => {
        obj.data ^= ((obj.data >> 5) | (obj.data << 3));
    });
}
    
async function callReadFileSync(obj, mutex, range) {
    const release = await mutex.lock();
    const chunk = fs.readFileSync('input');
    obj.data ^= chunk[range%32];
    release();
}
```

Which looks simple enough. There is one tricky part to it though: The order of the operations is not obvious. The reason for this is the JavaScript event loop and when what is executed. For example, `setImmediate` will be executed before `setTimeout(..., 0)` and `callNextTick` should be executed even before that, but after the actual inline statement in `case 2`. At the time of solving the challenge, it was not obvious to me that there was no context-switch between `case 1` and `case 2`, such that I thought the order should be: [7, 4, 6, 5] (naming the operations by the right-shift-value). However, that turned out to be incorrect so in order to not lose more time on this, I decided to see if I could brute-force the order by testing all possible permutations, which actually worked! For some characters, multiple permutations worked, so I had to implement a break condition. The most common permutation was [6, 5, 4, 7], suggesting that there is no context-switch between `case 1` and `case 2` after all.

# Solution

Finally, the solution coded in python can be seen below:


```python
import string
import itertools


# List of lambda functions for the transformations
transformations = [
    {"name": 7, "fn": lambda data: data ^ ((data >> 7) | (data << 1))},
    {"name": 4, "fn": lambda data: data ^ ((data >> 4) | (data << 4))},
    {"name": 6, "fn": lambda data: data ^ ((data >> 6) | (data << 2))},
    {"name": 5, "fn": lambda data: data ^ ((data >> 5) | (data << 3))}
]

integer_values = [
    3895813, 3893664, 3895583, 3893639, 3919755, 3893694, 3871506, 3871544,
    3810527, 3921672, 3913158, 3813122, 3869603, 3813209, 3910936, 3911023,
    3896081, 3822626, 3913160, 3919793, 3822653, 3895614, 3820987, 3820987, # 3820987 is listed twice, included once if unique is needed
    3932159, 3911025, 3893657, 3921671, 3820578, 3921709, 3921698, 3910918
]

flag = []

for entry, idx in zip(integer_values[::-1], reversed(range(2304 - len(integer_values), 2304))):
    # print(idx, entry)
    found = False

    for permutation in itertools.permutations(transformations): # perm:
        if found:
            break

        for chr in string.printable:
            inputval = ord(chr)

            data = idx ^ inputval
            transformed_data = data

            for transform in permutation:
                transformed_data = transform["fn"](transformed_data)

            if transformed_data == entry:
                flag.append(chr)
                found = True
                print(f"Hooray, its {chr}, the permutations is {[transform['name'] for transform in permutation]}")
                break

print("".join(flag[::-1]))

```

    Hooray, its }, the permutations is [6, 5, 4, 7]
    Hooray, its l, the permutations is [6, 5, 4, 7]
    Hooray, its l, the permutations is [6, 5, 4, 7]
    Hooray, its 3, the permutations is [6, 5, 4, 7]
    Hooray, its h, the permutations is [6, 5, 4, 7]
    Hooray, its _, the permutations is [6, 5, 4, 7]
    Hooray, its p, the permutations is [6, 5, 4, 7]
    Hooray, its o, the permutations is [7, 6, 5, 4]
    Hooray, its 0, the permutations is [6, 5, 4, 7]
    Hooray, its 1, the permutations is [6, 5, 4, 7]
    Hooray, its _, the permutations is [6, 5, 4, 7]
    Hooray, its 7, the permutations is [6, 5, 4, 7]
    Hooray, its n, the permutations is [6, 5, 4, 7]
    Hooray, its v, the permutations is [6, 5, 4, 7]
    Hooray, its 3, the permutations is [6, 5, 4, 7]
    Hooray, its _, the permutations is [7, 6, 5, 4]
    Hooray, its d, the permutations is [6, 5, 4, 7]
    Hooray, its n, the permutations is [6, 5, 4, 7]
    Hooray, its 4, the permutations is [6, 5, 4, 7]
    Hooray, its _, the permutations is [6, 5, 4, 7]
    Hooray, its 3, the permutations is [6, 5, 4, 7]
    Hooray, its l, the permutations is [6, 5, 4, 7]
    Hooray, its y, the permutations is [6, 5, 4, 7]
    Hooray, its 7, the permutations is [7, 6, 5, 4]
    Hooray, its S, the permutations is [6, 5, 4, 7]
    Hooray, its P, the permutations is [6, 5, 4, 7]
    Hooray, its C, the permutations is [6, 5, 4, 7]
    Hooray, its {, the permutations is [6, 5, 4, 7]
    Hooray, its D, the permutations is [6, 5, 4, 7]
    Hooray, its A, the permutations is [6, 5, 4, 7]
    Hooray, its E, the permutations is [6, 5, 4, 7]
    Hooray, its D, the permutations is [7, 6, 5, 4]
    DEAD{CPS7yl3_4nd_3vn7_10op_h3ll}



```python

```
