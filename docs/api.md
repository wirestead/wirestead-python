# API

The Python package exposes the pybind11 API migrated from the Wirestead C++ core
repository.

```python
import wirestead

client = wirestead.TcpClient("127.0.0.1", 9000)
server = wirestead.TcpServer(9000)
```

The compiled extension is installed as `wirestead._core`.

## Runtime statistics

Every transport exposes `stats()`, which returns a `RuntimeStats` snapshot, and
`reset_stats()`, which zeroes the counters. The snapshot is a copy taken at the
moment of the call, so holding on to one and taking another later gives you a
delta.

```python
stats = server.stats()
print(stats.bytes_received, stats.dropped_bytes, stats.backpressure_active)
```

| Field | Meaning |
|---|---|
| `bytes_accepted`, `messages_accepted` | What the application handed to the library |
| `bytes_sent`, `messages_sent` | What the socket actually wrote |
| `bytes_received`, `messages_received` | Read completions, not framed messages |
| `failed_sends` | Sends the library refused |
| `dropped_bytes`, `dropped_messages` | Discarded under `BackpressureStrategy.BestEffort` |
| `backpressure_events` | Congestion transitions observed |
| `queued_bytes`, `pending_bytes` | Currently outstanding |
| `max_queued_bytes` | High-water mark |
| `backpressure_active` | Whether congestion is on right now |

Two things are worth knowing before you read the numbers.

Byte totals reconcile between `*_accepted` and `*_sent`, but the message counts
do not, because queued writes are batched into fewer, larger socket writes.
`*_received` counts read completions for the same reason, so comparing it
against your own framed-message count is how you see framing at work.

Under `BackpressureStrategy.BestEffort`, `on_backpressure` is not a reliable
loss signal. Dropping is what holds the queue below the threshold that would
fire the callback, so whether it fires at all depends on how the queue happens
to cross that threshold: a server discarding hundreds of megabytes can report
`backpressure_events == 0` the whole time. Watch `dropped_bytes` and
`dropped_messages` instead. Under the `Reliable` default the callback does fire
and nothing is dropped.

A server's `stats()` aggregates its live sessions, so the counters fall back to
zero once every client has disconnected. Keep your own totals if you need
numbers that survive connection churn.
