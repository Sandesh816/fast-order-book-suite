# Fast Order Book Benchmark & Async gRPC Risk Gateway

High Performance C++17 **limit order book benchmark** (RB-tree / sorted-vector / hash + lazy-heaps) + a **Python order gateway** (synchronous and async `grpc.aio` variants) forwarding orders to the engine over gRPC. The project demonstrates *data structure latency trade-offs* inside the matching core engine **and** *application-layer latency* introduced by a risk layer + RPC boundary.

---

## 1. Components Overview

| Layer | Tech | Purpose |
|-------|------|---------|
| Matching Engine | C++17, custom data structures | Maintain bid/ask books; benchmark structural choices |
| Engine gRPC Service | C++17 + gRPC (`EngineInternal`) | Exposes minimal RPCs: Limit, Market, Cancel, Top |
| Risk Gateway (Sync) | Python + `grpc` threads | Validates & enriches client orders, forwards to engine |
| Risk Gateway (Async) | Python + `grpc.aio` | Lower-overhead asynchronous variant (current default) |
| Client Bench Tool | Python (`grpc.aio`) | Sends orders, measures end-to-end latency & throughput |

---

## 2. Matching Engine Data Structures

Three interchangeable implementations of `IOrderBook`:

| Variant | Internal Structure | Core Characteristics | Best-Price Maintenance Strategy |
|---------|--------------------|----------------------|----------------------------------|
| `map` | `std::map` (RB-tree) | O(log n) inserts, ordered iteration | `begin()` / `rbegin()` |
| `vector` | Manually maintained sorted `std::vector` | Binary search + O(n) shifts, excellent cache locality | Front element (bids desc / asks asc) |
| `hash` (optimized) | `std::unordered_map` + lazy min/max heaps + active sets | Amortized O(1) insert/update, O(log n) heap pops only when best changes | Lazy heaps purge stale prices |

### Engine Benchmark Methodology

- **Events**: 500,000 synthetic (default)  
- **Mix**: 60% limit orders, 25% market orders, 15% cancel  
- **Price**: N(10,000, 80), **Qty**: U[1,100]  
- **Build**: `-O3 -march=native -DNDEBUG`  
- **Seed**: 42  
- **Platform**: macOS (Apple M1 Pro 8-core)

### Multi-Trial Engine Results (5x runs @500k events)

| Variant | Mean Throughput (events/s) | Median (ns) | p95 (ns) | p99 (ns) | Notes |
|---------|----------------------------|------------:|---------:|---------:|-------|
| map (RB-tree) | 8.85M | 42 | ~90–125 | ~166–208 | Consistent |
| vector (sorted) | 8.58M | 42 | 125 | 167 | Occasional O(n) shifts in tail |
| hash (lazy heaps) | **10.39M** | 42 | 125 | 209–250 | Heavily optimized & Tail collapsed vs naive |

**Naive hash (pre-optimization)** for comparison (single run): 5.2M events/s, p99 1.29 µs — *tail dominated by full scans*. Optimization (lazy heaps + active price sets) cut p99 ≈5× and +~2× throughput.

---

## 3. Risk Gateway (gRPC)

| Aspect | Implementation |
|--------|---------------|
| Public Service | `GatewayPublic` (SubmitLimit / SubmitMarket / SubmitCancel / Top / Stats / Reset) |
| Engine Bridge | Calls `EngineInternal` RPCs (Limit / Market / Cancel / Top) |
| Risk Checks | Quantity (0<qty≤500), ±5% price collar (vs synthetic mid=10,000), cumulative notional ≤50M, net position tracking |
| State Mutation | Only on accepted orders (rejects are side-effect free) |
| Metadata Added | `gateway_order_id` (UUID), `recv_unix_ns`, `risk_status` |
| Latency Sampling | Per accepted order (ring buffer, default 4096 samples) |
| Reset Capability | Full or per-client state wipe via `Reset` RPC |
| Async Advantage | Lower thread context switching, easy concurrent pipelining |

---

## 4. Gateway Benchmarks (Async `grpc.aio` Prototype)

**Config:** 50 random accepted warm-up orders → stats → 600 limit orders (80 warm-up inside bench), concurrency=4.

| Metric | Value (Sample Run) |
|--------|---------------------|
| Median latency | 997 µs |
| p95 latency | 1.22 ms |
| p99 latency | 1.44 ms |
| Min / Max | 0.50 ms / 1.78 ms |
| Throughput (bench phase) | ~3.4 K ops/s |
| Gateway Stats (pre-bench) | 50 total, 0 rejects |
| Gateway Stats (post-bench) | 730 total, 180 rejects (includes subsequent tests) |

---

## 6. How to Build & Run

### 6.1 Engine & Engine gRPC (C++)

```bash
# From repo root
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
./build/engine_grpc/engine_server
