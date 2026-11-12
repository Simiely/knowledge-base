"""最小真源示例：运行时配置。

规范里的 ground truth 从这里抽取，不从文档抽取。
改这里的键而不改 docs/config.md，CI 会报 TRUTH_DRIFT。
"""
SETTINGS = {
    "retry_max": 3,
    "timeout_ms": 5000,
    "cache_ttl": 600,
    "maxRetries": 9,
}
