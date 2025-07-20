import asyncio
import random
import time
import statistics
import grpc
import order_pb2, order_pb2_grpc

RANDOM_ORDERS = 50

async def random_orders(stub):
    for i in range(RANDOM_ORDERS):
        req = order_pb2.SubmitLimitRequest(
            client_id="c_demo",
            is_buy=bool(i & 1),
            price=10000 + random.randint(-40, 40),
            qty=random.randint(1, 50)
        )
        ack = await stub.SubmitLimit(req)
        print(f"{i:02d} ok={ack.ok} status={ack.message}")

async def latency_bench(stub, n=500, warmup=50, concurrent=1):
    # Warm-up
    for _ in range(warmup):
        await stub.SubmitLimit(order_pb2.SubmitLimitRequest(
            client_id="bench",
            is_buy=True,
            price=10000,
            qty=10
        ))

    lat = []

    async def one_call():
        t0 = time.time_ns()
        await stub.SubmitLimit(order_pb2.SubmitLimitRequest(
            client_id="bench",
            is_buy=True,
            price=10000,
            qty=10
        ))
        lat.append((time.time_ns() - t0)/1000.0)

    t_batch0 = time.time_ns()
    if concurrent == 1:
        for _ in range(n):
            await one_call()
    else:
        # batched concurrency
        batch = []
        for i in range(n):
            batch.append(asyncio.create_task(one_call()))
            if len(batch) >= concurrent:
                await asyncio.gather(*batch)
                batch.clear()
        if batch:
            await asyncio.gather(*batch)
    t_batch1 = time.time_ns()

    lat_sorted = sorted(lat)
    def pct(p):
        k = (len(lat_sorted)-1)*p
        i = int(k); f = k - i
        if i+1 < len(lat_sorted):
            return lat_sorted[i]*(1-f)+lat_sorted[i+1]*f
        return lat_sorted[i]

    total_us = (t_batch1 - t_batch0)/1000.0
    throughput = n * 1_000_000.0 / total_us
    return {
        "median": pct(0.50),
        "p95": pct(0.95),
        "p99": pct(0.99),
        "min": lat_sorted[0],
        "max": lat_sorted[-1],
        "throughput_ops_per_s": throughput,
        "samples": len(lat_sorted)
    }

async def main():
    channel = grpc.aio.insecure_channel("localhost:6000")
    stub = order_pb2_grpc.GatewayPublicStub(channel)

    # Reset all state
    await stub.Reset(order_pb2.ResetRequest())

    print("Random order burst:")
    await random_orders(stub)

    top = await stub.Top(order_pb2.TopRequest())
    stats = await stub.Stats(order_pb2.StatsRequest())
    print(f"Top: bid={top.best_bid} ask={top.best_ask}")
    print(f"Stats pre-bench: total={stats.total_orders} rejected={stats.total_rejected} avg_us={stats.avg_latency_us:.2f}")

    bench = await latency_bench(stub, n=600, warmup=80, concurrent=4)
    print("Latency Bench (async gateway → engine):")
    print(" median={median:.2f}us p95={p95:.2f}us p99={p99:.2f}us "
          "min={min:.2f}us max={max:.2f}us throughput={throughput_ops_per_s:.0f} ops/s (samples={samples})"
          .format(**bench))

    stats2 = await stub.Stats(order_pb2.StatsRequest())
    print(f"Stats post-bench: total={stats2.total_orders} rejected={stats2.total_rejected} "
          f"avg_us={stats2.avg_latency_us:.2f} p95={stats2.p95_latency_us:.2f} p99={stats2.p99_latency_us:.2f}")

    await channel.close()

if __name__ == "__main__":
    asyncio.run(main())