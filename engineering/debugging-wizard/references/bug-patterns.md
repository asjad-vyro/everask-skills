# Bug patterns and common error messages

Read this when the symptom matches a row. Confirm the pattern against the user's code before naming it as the cause.

## Symptom to first check

| Symptom | First check |
|---|---|
| "undefined is not..." / "NoneType has no attribute" / KeyError | A value that can be missing is used without a check; trace where it was set |
| Works sometimes, fails sometimes | Race condition, missing await, shared mutable state, timing |
| Wrong value inside a callback | Closure capture in a loop, or stale state |
| Slower with more data | N+1 queries, query inside a loop, missing index |
| Memory grows over time | Listeners, intervals, caches or connections never released |
| Misses the first or last item | Loop bound (`<` vs `<=`), index `length` vs `length - 1` |
| Unexpected equality or type behaviour | `==` vs `===`, string vs number, timezone or encoding |
| Fails only in production | Environment variables, versions, data differences, permissions, network or proxy |
| Timeouts under load | Connection pool exhausted, slow downstream call, no timeout set, retry storm |

## Patterns with the usual fix

**Missing await or race (JavaScript)**: `fetchData().then(r => { data = r }); use(data)` reads before it is set. Fix: `const data = await fetchData();`. `items.forEach(async ...)` does not wait; use `for (const item of items) { await ... }` or `await Promise.all(items.map(...))`.

**Null or undefined access**: `user.profile.name` fails if either is missing. Fix at the source where possible (return a default, validate input); otherwise `user?.profile?.name ?? fallback`. In Python use `.get()` with a default, or check for `None` first, but ask why the key is missing before hiding it.

**Off by one**: loop `i < arr.length - 1` skips the last item; `arr[arr.length]` is out of range. Last element is `arr[arr.length - 1]`.

**Closure in a loop**: `for (var i...) setTimeout(() => log(i))` prints the final value. Use `let`, or pass the value in.

**React stale state**: `setCount(count + 1)` inside an interval created on mount always sees the first `count`. Use `setCount(c => c + 1)` and clear the interval in the effect cleanup. Setting state during render causes "too many re-renders"; move it into an effect or an event handler. An object or array literal in a dependency array changes every render; memoize it or use primitives.

**Leaks**: `addEventListener` without `removeEventListener`, `setInterval` without `clearInterval`, unbounded caches, unclosed files or connections. Release in a cleanup, `finally` or `with` block.

**Unhandled promise rejection**: add `.catch(...)` or wrap the `await` in `try/catch`, and decide what the caller should see.

**Infinite recursion ("Maximum call stack", RecursionError)**: no base case, or the argument never moves toward it. Circular object references break `JSON.stringify`; break the cycle or use a replacer.

**Module not found**: wrong relative path (`./x` vs `x`), missing install, missing extension in ESM, wrong working directory, or a virtual environment that is not the one in use.

**CORS error**: the browser blocks a cross-origin response lacking the right headers. Fix on the server (allow the specific origin, and credentials if used), or proxy in development. The request itself often succeeded.

**`await` in a non-async function**: mark the function `async`.

**Python specifics**: `KeyError` means the dict has no such key (print `d.keys()` at that point); `TypeError: 'NoneType'` usually means a function returned None implicitly; mutable default arguments (`def f(x, acc=[])`) share state across calls; `IndexError` on an empty list.

**SQL errors**: read the database's position or line marker, check column and table names and quoting, type mismatches in comparisons, a missing GROUP BY column, and whether the production schema or data differs from local.
