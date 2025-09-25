#!/usr/bin/env python
"""
Phase-1 Async Worker
Processes permutation jobs from Redis queue
"""

import os
import json
import time
import heapq
import itertools as _it
import redis
from datetime import datetime

# Import from phase1_flask_integration
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from phase1_flask_integration import (
        _build_grid, _evaluate_perm,
        QUEUE_KEY, JOB_KEY, RES_KEY
    )
except ImportError:
    print("Error: Could not import from phase1_flask_integration")
    sys.exit(1)

# Redis connection
rds = redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/2"))
CHUNK = int(os.getenv("PHASE1_CHUNK", "10000"))

def update(job_id, **fields):
    """Update job metadata in Redis"""
    to_set = {}
    for k, v in fields.items():
        to_set[k] = json.dumps(v) if isinstance(v, (dict, list)) else str(v)
    rds.hset(JOB_KEY.format(job_id=job_id), mapping=to_set)

def run_job(job_id):
    """Process a single job"""
    print(f"[WORKER] Starting job {job_id}")

    # Load job metadata
    h = {k.decode(): v.decode() for k, v in rds.hgetall(JOB_KEY.format(job_id=job_id)).items()}
    seed = int(h.get("seed", 424242))
    topn = int(h.get("topn", 20))
    ranges = json.loads(h["ranges"])
    keys, values, card, _ = _build_grid(ranges)

    update(job_id, status="running", started_at=datetime.utcnow().isoformat(), processed=0, total=card)
    print(f"[WORKER] Job {job_id}: Processing {card:,} permutations")

    counter = _it.count(0)
    heap = []
    processed = 0

    # Process all permutations
    for combo in _it.product(*[values[i] for i in range(len(values))]):
        perm = dict(zip(keys, combo))
        res = _evaluate_perm(perm, seed)
        score = res["day_one_value_total"]
        entry = (score, next(counter), res)

        if len(heap) < topn:
            heapq.heappush(heap, entry)
        else:
            heapq.heappushpop(heap, entry)

        processed += 1

        # Update progress periodically
        if processed % CHUNK == 0 or processed == card:
            pct = int(processed * 100 / card) if card else 100
            update(job_id, processed=processed, progress_pct=pct)
            print(f"[WORKER] Job {job_id}: {pct}% complete ({processed:,}/{card:,})")

    # Extract top structures
    top_structs = []
    for rank, (score, _, struct) in enumerate(sorted(heap, key=lambda t: (t[0], t[1]), reverse=True), 1):
        struct["rank"] = rank
        top_structs.append(struct)

    # Count tiers
    diamond_count = sum(1 for s in top_structs if s.get("tier") == "Diamond")
    gold_count = sum(1 for s in top_structs if s.get("tier") == "Gold")
    silver_count = sum(1 for s in top_structs if s.get("tier") == "Silver")

    stats = {
        "total_permutations": processed,
        "diamond_count": diamond_count,
        "gold_count": gold_count,
        "silver_count": silver_count,
        "gate_a_pruned": 0,
        "gate_b_pruned": 0,
        "near_misses": sum(1 for s in top_structs if s.get("near_miss") == "Y")
    }

    result = {
        "message": f"Processed {processed:,} permutations",
        "stats": stats,
        "top_structures": top_structs,
        "completed_at": datetime.utcnow().isoformat()
    }

    # Store results
    rds.set(RES_KEY.format(job_id=job_id), json.dumps(result))
    update(job_id, status="done", progress_pct=100, finished_at=datetime.utcnow().isoformat())

    print(f"[WORKER] Job {job_id}: Complete! Top value: {top_structs[0]['day_one_value_total'] if top_structs else 0}")

def main():
    """Main worker loop"""
    print("[WORKER] Phase-1 async worker started")
    print(f"[WORKER] Redis: {os.environ.get('REDIS_URL', 'redis://localhost:6379/2')}")
    print(f"[WORKER] Chunk size: {CHUNK:,}")
    print("[WORKER] Waiting for jobs...")

    while True:
        try:
            # Block waiting for job (5 second timeout)
            popped = rds.blpop(QUEUE_KEY, timeout=5)
            if not popped:
                continue

            _, payload = popped
            job = json.loads(payload.decode())
            job_id = job["job_id"]

            try:
                run_job(job_id)
            except Exception as e:
                print(f"[WORKER] Job {job_id} failed: {e}")
                update(job_id, status="error", error=str(e))

        except KeyboardInterrupt:
            print("[WORKER] Shutting down...")
            break
        except Exception as e:
            print(f"[WORKER] Error in main loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()