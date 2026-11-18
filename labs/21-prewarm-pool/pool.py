from dataclasses import dataclass, field


@dataclass
class Environment:
    environment_id: str
    created_at: int
    prewarm_ttl: int = 300
    idle_ttl: int = 1200
    checkpoint_ttl: int = 7 * 24 * 3600
    max_sessions: int = 128
    sessions: set[str] = field(default_factory=set)
    state: str = "PREWARMED"
    idle_deadline: int | None = None
    checkpoint_deadline: int | None = None


class PrewarmPool:
    def __init__(self):
        self.environments: dict[str, Environment] = {}

    def create(self, environment_id: str, now: int) -> Environment:
        env = Environment(environment_id=environment_id, created_at=now)
        self.environments[environment_id] = env
        return env

    def attach(self, environment_id: str, session_id: str, now: int) -> None:
        env = self.environments[environment_id]
        if env.state == "PREWARMED" and now > env.created_at + env.prewarm_ttl:
            env.state = "EXPIRED"
            raise RuntimeError("unattached prewarm environment expired")
        if env.state in {"EXPIRED", "DELETED"}:
            raise RuntimeError(f"environment is {env.state.lower()}")
        if session_id in env.sessions:
            return
        if len(env.sessions) >= env.max_sessions:
            raise RuntimeError("session limit reached")
        if env.state == "SUSPENDED":
            if env.checkpoint_deadline is None or now > env.checkpoint_deadline:
                env.state = "EXPIRED"
                raise RuntimeError("checkpoint expired")
            env.state = "ATTACHED"
        else:
            env.state = "ATTACHED"
        env.sessions.add(session_id)
        env.idle_deadline = now + env.idle_ttl

    def activity(self, environment_id: str, session_id: str, now: int) -> None:
        env = self.environments[environment_id]
        if env.state != "ATTACHED" or session_id not in env.sessions:
            raise RuntimeError("session is not attached")
        env.idle_deadline = now + env.idle_ttl

    def detach(self, environment_id: str, session_id: str, now: int) -> None:
        env = self.environments[environment_id]
        env.sessions.discard(session_id)
        if not env.sessions and env.state == "ATTACHED":
            env.idle_deadline = now + env.idle_ttl

    def tick(self, environment_id: str, now: int) -> str:
        env = self.environments[environment_id]
        if env.state == "PREWARMED" and now > env.created_at + env.prewarm_ttl:
            env.state = "EXPIRED"
        elif env.state == "ATTACHED" and env.idle_deadline is not None and now >= env.idle_deadline:
            env.state = "SUSPENDED"
            env.sessions.clear()
            env.checkpoint_deadline = now + env.checkpoint_ttl
        elif env.state == "SUSPENDED" and env.checkpoint_deadline is not None and now > env.checkpoint_deadline:
            env.state = "EXPIRED"
        return env.state

    def delete(self, environment_id: str) -> None:
        env = self.environments[environment_id]
        env.state = "DELETED"
        env.sessions.clear()
