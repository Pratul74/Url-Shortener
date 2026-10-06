import time
import threading
import asyncio

class IDGenerator:
    EPOCH = 1767225600000
    WORKER_BITS=10
    SEQ_BITS=12
    MAX_WORKER=(1<<WORKER_BITS)-1
    MAX_SEQ=(1<<SEQ_BITS)-1
    MAX_DRIFT_MS=5

    def __init__(self, worker_id: int):
        if not 0 <= worker_id <= self.MAX_WORKER:
            raise ValueError(f"worker_id must be 0..{self.MAX_WORKER}")
        self.worker_id=worker_id
        self.last_ts=-1
        self.seq=0
        self._lock=threading.Lock()

    @staticmethod
    def _get_ms():
        return time.time_ns()//1000_000

    async def _try_next_id(self) -> tuple[int | None, float]:
        with self._lock:
            ts = self._get_ms()

            if ts<self.last_ts:
                drift = self.last_ts-ts
                if drift>self.MAX_DRIFT_MS:
                    raise RuntimeError(f"Clock moved backwards by {drift}ms")
                return None, drift/1000
            if ts == self.last_ts:
                self.seq = (self.seq + 1) & self.MAX_SEQ
                if self.seq==0:
                    return None, 0.001
            else:
                self.seq=0
            self.last_ts = ts
            new_id = (
                (self.last_ts - self.EPOCH) << (self.SEQ_BITS + self.WORKER_BITS)
                | self.worker_id << self.SEQ_BITS
                | self.seq
            )
            return new_id, 0

    async def next_id(self) -> int:
        while True:
            new_id, wait = await self._try_next_id()
            if new_id is not None:
                return new_id
            await asyncio.sleep(wait)


