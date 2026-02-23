# Rate Limiting

The Kanka API enforces rate limits to prevent abuse:

- **Free users:** 30 requests per minute
- **Subscribers:** 90 requests per minute

The SDK handles rate limits automatically by default.

## Default Behavior

When a request receives a `429 Too Many Requests` response, the SDK:

1. Parses the `Retry-After` header (or `X-RateLimit-Remaining` / `X-RateLimit-Reset` headers) to determine the optimal wait time
2. Waits for the specified delay
3. Retries the request
4. Doubles the delay for each subsequent retry (exponential backoff), up to `max_retry_delay`
5. Gives up after `max_retries` attempts, raising `RateLimitError`

This is enabled by default — no configuration needed:

```python
from kanka import KankaClient

client = KankaClient(token="...", campaign_id=12345)
# Rate limit retries happen automatically
```

## Configuration

### Disabling Auto-Retry

```python
client = KankaClient(
    token="...",
    campaign_id=12345,
    enable_rate_limit_retry=False,
)
# Now RateLimitError is raised immediately on 429 responses
```

### Customizing Retry Behavior

| Parameter | Default | Description |
|-----------|---------|-------------|
| `enable_rate_limit_retry` | `True` | Whether to retry on rate limits |
| `max_retries` | `8` | Maximum number of retry attempts |
| `retry_delay` | `1.0` | Initial delay between retries (seconds) |
| `max_retry_delay` | `15.0` | Maximum delay between retries (seconds) |

```python
client = KankaClient(
    token="...",
    campaign_id=12345,
    max_retries=5,
    retry_delay=2.0,
    max_retry_delay=30.0,
)
```

## How Retry Delays Are Calculated

1. **First choice:** The `Retry-After` header value (seconds until rate limit resets)
2. **Second choice:** Computed from `X-RateLimit-Remaining` (0) and `X-RateLimit-Reset` (Unix timestamp)
3. **Fallback:** The configured `retry_delay`, doubling with each attempt (exponential backoff)

The delay is always capped at `max_retry_delay`.

## When to Customize

- **Bulk operations** (creating hundreds of entities): Increase `max_retries` and `max_retry_delay` to wait longer
- **Tight latency requirements**: Decrease `max_retries` or disable auto-retry to fail fast
- **Subscriber accounts**: May lower `retry_delay` since rate limits are more generous
