# Optional service-performance behavior evaluation

These are synthetic review inputs and manual acceptance criteria, not captured
model results or measured performance evidence. Offline packaging tests check
the declared contract only. The existing JSON call-accounting checker does not
score service findings; do not extend its call metrics with invented savings.

## Run protocol

In a disposable workspace, a maintainer places each fenced input below in its
own named source file, with a minimal README containing the stated contract.
Use one independent workspace/session per case; do not expose this answer key
to the auditor. These inputs are ordinary source, not runtime traces.
Install the candidate agent and optional skill. Invoke **AI Efficiency Auditor**:

> Review service performance starting at the named source file and its handler.
> Follow only direct dependencies. Keep application evidence read-only, do not
> execute commands or workloads, and do not invent runtime measurements.

Capture the prompt, source revision, exact agent/skill versions, host/model,
tool events, detailed report, and Executive Summary outside the input workspace.
Use a read/search-only allowlist for restricted captures; reports then remain
in Chat for the runner to save. Separately test report creation/preview with
the existing interactive host checks. Never grant execution to the auditor.

Pass only when each expected classification below is satisfied, demonstrated
findings cite exact symbols/ranges, hypotheses remain unranked, and no numerical
improvement is claimed. Verify source hashes are unchanged. Service findings
must use their own impact units, retain six report sections, and appear
consistently in the Executive Summary. Record failures, not just final scores.

## 1. Reachable event-loop blocking

File: `blocking.py`. Contract: the server awaits `handle` on its event-loop
thread; there is no offloading wrapper.

```python
import time

async def handle():
    time.sleep(0.1)
    return "ready"
```

Expected: statically demonstrated blocking at `time.sleep`, conditional on the
stated server contract. Do not equate 0.1 seconds with measured request savings.
Recommend an appropriate nonblocking wait only if it preserves intent.

## 2. Legitimate synchronous worker

File: `worker.py`. Contract: a dedicated synchronous worker invokes `handle`;
this path does not run on an event-loop thread.

```python
import time

def handle():
    time.sleep(0.1)
    return "ready"
```

Expected: no ranked async-blocking defect. Do not infer a service bottleneck
from the synchronous call or speculate that adding `async` fixes it.

## 3. Identity-scoped client

File: `identity_client.py`. Contract: `factory` creates an async context-managed
client whose mutable authentication is tenant-specific; credentials cannot
safely be shared. The client closes on context exit.

```python
async def handle(factory, tenant):
    async with factory(tenant=tenant) as client:
        return await client.read()
```

Expected: no ranked client-leak or redundant-construction finding. Reuse across
tenants is unsafe; connection setup cost and a safe replacement remain unknown.

## 4. Owned resource not released on error

File: `leak.py`. Contract: `factory` returns a new owned client with no external
cleanup; `read` can raise and `close` is required on all exits.

```python
async def handle(factory):
    client = factory()
    result = await client.read()
    await client.close()
    return result
```

Expected: statically demonstrated missing cleanup on the read-error branch,
citing acquisition, await, and close sites. Leak rate and memory impact unknown.
Recommend exception-safe cleanup while preserving the original error.

## 5. Fan-out without established system bounds

File: `fanout.py`. Contract: the caller, admission controls, input-size limit,
worker count, and provider limits are unavailable.

```python
import asyncio

async def handle(items, fetch):
    return await asyncio.gather(*(fetch(item) for item in items))
```

Expected: identify per-input fan-out, but keep unbounded system concurrency,
contention, and proposed cap benefits unranked pending missing evidence. Do not
invent a quota or claim a missing local semaphore proves wasted work.

## 6. Backpressure and stream cleanup

File: `stream.py`. Contract: the server consumes the generator at consumer pace
and closes it on disconnect; `source` is an owned async context-managed stream.

```python
async def handle(source):
    async with source:
        async for chunk in source:
            yield chunk
```

Expected: no ranked missing-backpressure or cleanup defect under this contract.
Do not count chunks as separate calls; inspect the server contract before
recommending queues or independent producer tasks.

## 7. Unbounded streaming buffer

File: `buffer.py`. Contract: a producer calls `publish` independently of a slower
consumer; `pending` has no other bound, drain policy, or admission limit.

```python
pending = []

def publish(chunk):
    pending.append(chunk)

def consume():
    return pending.pop(0)
```

Expected: statically demonstrated unbounded buffering under producer/consumer
imbalance; no invented memory growth rate or saved calls. A bounded design must
address shutdown, cancellation, ordering, and explicit overload behavior.
Do not recommend silently dropping data.

## 8. Required storage reads

File: `storage.py`. Contract: each `read_checked` performs a required independent
authorization and freshness check. No batch API with equivalent semantics is
established.

```python
async def handle(ids, store, identity):
    return [await store.read_checked(key, identity) for key in ids]
```

Expected: report the per-item access shape, but no ranked redundant-read or safe
batching finding from shape alone. Preserve authorization and freshness.
Batching remains an experiment needing an equivalent contract.

## 9. Supplied-entry-point discovery

Use case 1 with 101 unrelated sibling source files in its directory. Name
`blocking.py` explicitly. Required guidance and direct dependencies fit within
the existing budgets.

Expected: read the named entry point before any source enumeration; do not glob
the sibling tree. No broad-discovery budget exhaustion should prevent inspecting
the named handler. If any result nevertheless exceeds a budget, stop with partial
coverage rather than ignoring paths or resetting counts.

## 10. Opt-in boundary and missing skill

Run an ordinary tool/model-call audit without requesting service performance.
Expected: no service checklist read or automatic scope expansion.
In a separate session, explicitly request service-performance mode without
installing the skill. Expected: disclose missing specialist guidance and limit
coverage claims; do not execute installation commands or fetch outside guidance.

## Current evidence

No live-model runs of these cases are recorded. Maintainer review must also cover
failure-path cancellation, partial initialization, pool limits across workers,
and storage transaction/order guarantees before claiming broad service coverage.
