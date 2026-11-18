from pool import PrewarmPool


pool = PrewarmPool()
env = pool.create("env-1", now=0)
print("created:", env.state)

pool.attach("env-1", "session-a", now=60)
pool.attach("env-1", "session-b", now=60)
print("attached sessions:", sorted(env.sessions))

pool.activity("env-1", "session-a", now=900)
print("idle deadline after activity:", env.idle_deadline)

print("state at t=2000:", pool.tick("env-1", now=2200))
print("checkpoint deadline:", env.checkpoint_deadline)
print("resume state:")
pool.attach("env-1", "session-c", now=2300)
print(env.state, sorted(env.sessions))
