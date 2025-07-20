import asyncio
import time
import uuid
import signal
import grpc
import order_pb2
import order_pb2_grpc
from collections import deque

MAX_ORDER_QTY = 500
MAX_NOTIONAL = 50_000_000         # cumulative per client for now
PRICE_COLLAR_PCT = 5.0
MID_PRICE = 10_000

client_notional = {}
client_positions = {}

LAT_SAMPLE_MAX = 4096
lat_samples_us = deque(maxlen=LAT_SAMPLE_MAX)

total_orders = 0
total_rejected = 0
lat_sum_us = 0.0

def risk_check_limit(client_id: str, is_buy: bool, price: int, qty: int):
    if qty <= 0:
        return False, "BAD_QTY", 0, 0
    if qty > MAX_ORDER_QTY:
        return False, "QTY_LIMIT", 0, 0
    if abs(price - MID_PRICE) / MID_PRICE * 100.0 > PRICE_COLLAR_PCT:
        return False, "PRICE_COLLAR", 0, 0
    current_notional = client_notional.get(client_id, 0)
    add_notional = price * qty
    if current_notional + add_notional > MAX_NOTIONAL:
        return False, "NOTIONAL_LIMIT", 0, 0
    pos_delta = qty if is_buy else -qty
    return True, "OK", add_notional, pos_delta

def record_latency(us: float):
    global lat_sum_us
    lat_sum_us += us
    lat_samples_us.append(us)

def percentile(data, p):
    if not data:
        return 0.0
    arr = sorted(data)
    k = (len(arr) - 1) * p
    i = int(k)
    f = k - i
    if i + 1 < len(arr):
        return arr[i] * (1 - f) + arr[i + 1] * f
    return arr[i]

class GatewayService(order_pb2_grpc.GatewayPublicServicer):
    def __init__(self, engine_stub):
        self.engine = engine_stub

    async def SubmitLimit(self, request, context):
        global total_orders, total_rejected
        t0 = time.time_ns()
        ok, status, add_notional, pos_delta = risk_check_limit(
            request.client_id, request.is_buy, request.price, request.qty
        )
        meta = order_pb2.OrderMeta(
            client_id=request.client_id,
            gateway_order_id=str(uuid.uuid4()),
            recv_unix_ns=t0,
            risk_status=status
        )
        total_orders += 1
        if not ok:
            total_rejected += 1
            return order_pb2.Ack(ok=False, message=status, meta=meta)

        client_notional[request.client_id] = client_notional.get(request.client_id, 0) + add_notional
        client_positions[request.client_id] = client_positions.get(request.client_id, 0) + pos_delta

        ack = await self.engine.Limit(order_pb2.LimitOrder(
            is_buy=request.is_buy,
            price=request.price,
            qty=request.qty,
            meta=meta
        ))
        elapsed_us = (time.time_ns() - t0) / 1000.0
        record_latency(elapsed_us)
        return ack

    async def SubmitMarket(self, request, context):
        global total_orders, total_rejected
        t0 = time.time_ns()
        ok, status, add_notional, pos_delta = risk_check_limit(
            request.client_id, request.is_buy, MID_PRICE, request.qty
        )
        meta = order_pb2.OrderMeta(
            client_id=request.client_id,
            gateway_order_id=str(uuid.uuid4()),
            recv_unix_ns=t0,
            risk_status=status
        )
        total_orders += 1
        if not ok:
            total_rejected += 1
            return order_pb2.Ack(ok=False, message=status, meta=meta)

        client_notional[request.client_id] = client_notional.get(request.client_id, 0) + add_notional
        client_positions[request.client_id] = client_positions.get(request.client_id, 0) + pos_delta

        ack = await self.engine.Market(order_pb2.MarketOrder(
            is_buy=request.is_buy,
            qty=request.qty,
            meta=meta
        ))
        elapsed_us = (time.time_ns() - t0) / 1000.0
        record_latency(elapsed_us)
        return ack

    async def SubmitCancel(self, request, context):
        global total_orders
        t0 = time.time_ns()
        meta = order_pb2.OrderMeta(
            client_id=request.client_id,
            gateway_order_id=str(uuid.uuid4()),
            recv_unix_ns=t0,
            risk_status="OK"
        )
        total_orders += 1
        ack = await self.engine.Cancel(order_pb2.CancelOrder(
            is_buy=request.is_buy,
            price=request.price,
            qty=request.qty,
            meta=meta
        ))
        return ack

    async def Top(self, request, context):
        return await self.engine.Top(order_pb2.TopRequest())

    async def Stats(self, request, context):
        filled = total_orders - total_rejected
        avg = (lat_sum_us / filled) if filled > 0 else 0.0
        p50 = percentile(lat_samples_us, 0.50)
        p95 = percentile(lat_samples_us, 0.95)
        p99 = percentile(lat_samples_us, 0.99)
        return order_pb2.StatsReply(
            total_orders=total_orders,
            total_rejected=total_rejected,
            avg_latency_us=avg,
            p50_latency_us=p50,
            p95_latency_us=p95,
            p99_latency_us=p99
        )

    async def Reset(self, request, context):
        global total_orders, total_rejected, lat_sum_us
        cid = request.client_id.strip()
        if cid:
            client_notional.pop(cid, None)
            client_positions.pop(cid, None)
            # NOTE: we keep global counters if partial reset
        else:
            client_notional.clear()
            client_positions.clear()
            total_orders = 0
            total_rejected = 0
            lat_sum_us = 0.0
            lat_samples_us.clear()
        return order_pb2.ResetReply(ok=True)

async def serve():
    # Async channel to engine
    engine_channel = grpc.aio.insecure_channel(
        "localhost:50051",
        options=(
            ("grpc.keepalive_time_ms", 20000),
            ("grpc.keepalive_timeout_ms", 10000),
            ("grpc.http2.lookahead_bytes", 0),
            ("grpc.so_reuseport", 1),
            ("grpc.max_concurrent_streams", 1024),
        )
    )
    engine_stub = order_pb2_grpc.EngineInternalStub(engine_channel)

    server = grpc.aio.server(options=(
        ("grpc.so_reuseport", 1),
    ))
    order_pb2_grpc.add_GatewayPublicServicer_to_server(GatewayService(engine_stub), server)
    listen_addr = "0.0.0.0:6000"
    server.add_insecure_port(listen_addr)
    print(f"[gateway-async] listening on {listen_addr} (engine -> 50051)")
    await server.start()

    shutdown_event = asyncio.Event()

    def _signal_handler():
        shutdown_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _signal_handler)
        except NotImplementedError:
            pass  # Windows

    await shutdown_event.wait()
    print("[gateway-async] Shutting down...")
    await server.stop(grace=None)
    await engine_channel.close()

if __name__ == "__main__":
    asyncio.run(serve())