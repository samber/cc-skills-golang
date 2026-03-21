# Grafana Dashboards for Go Services

Install these community Grafana dashboards to monitor Go runtime performance out of the box. They visualize the metrics automatically exposed by `github.com/prometheus/client_golang` — no custom instrumentation needed.

## Recommended Dashboards

| Dashboard | ID | What it shows |
| --- | --: | --- |
| [Go Host & Runtime Metrics](https://grafana.com/grafana/dashboards/21221-go-host-runtime-metrics-dashboard/) | 21221 | Host metrics + Go runtime (goroutines, heap, GC, threads) in one view |
| [Go Processes](https://grafana.com/grafana/dashboards/6671-go-processes/) | 6671 | Multi-process comparison — CPU, memory, goroutines, GC across all Go services |
| [Go Metrics](https://grafana.com/grafana/dashboards/10826-go-metrics/) | 10826 | Focused Go runtime view — memory breakdown, GC pauses, allocations, goroutines |

## How to Install

1. In Grafana, go to **Dashboards > New > Import**
2. Enter the dashboard ID (e.g., `21221`) and click **Load**
3. Select your Prometheus data source and click **Import**

These dashboards require the default Go collector metrics (`go_goroutines`, `go_memstats_*`, `go_gc_duration_seconds`, `process_*`). If you use the Prometheus client library with default collectors, everything works out of the box.

## When to Use Each

- **21221** (Host & Runtime) — day-to-day monitoring of a single Go service alongside its host. Best as the default Go dashboard.
- **6671** (Go Processes) — comparing multiple Go services or replicas side by side. Useful during deployments to spot regressions across instances.
- **10826** (Go Metrics) — deep-diving into memory and GC behavior of a single service. Best for investigating performance issues.
