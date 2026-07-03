import json
import redis
from dashscope import Generation

# 连接 Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)


class RedisMemory:
    """基于 Redis 的对话记忆（支持多用户多会话）"""

    def __init__(self, session_id: str, system_prompt: str = "",
                 ttl: int = 7 * 24 * 3600):   # 默认 7 天过期
        self.session_id = session_id
        self.key = f"chat:session:{session_id}"
        self.ttl = ttl
        # 首次创建时写入 system
        if system_prompt and not r.exists(self.key):
            self._push({"role": "system", "content": system_prompt})

    def _push(self, msg: dict):
        r.rpush(self.key, json.dumps(msg, ensure_ascii=False))
        r.expire(self.key, self.ttl)   # 每次写入刷新过期时间

    def add(self, role: str, content: str):
        self._push({"role": role, "content": content})

    def load(self) -> list:
        raw = r.lrange(self.key, 0, -1)
        return [json.loads(m) for m in raw]

    def clear(self):
        r.delete(self.key)


# === 使用：每个用户独立 session ===
def chat(session_id: str, user_input: str) -> str:
    memory = RedisMemory(session_id, system_prompt="你是 helpful 助手")
    memory.add("user", user_input)

    resp = Generation.call(
        model='qwen-turbo',
        messages=memory.load(),
        result_format='message'
    )
    reply = resp.output.choices[0].message.content
    memory.add("assistant", reply)
    return reply


# 用户 A 的对话
print(chat("user_alice", "我叫 Alice，记住"))
print(chat("user_alice", "我叫什么？"))   # → 即使重启进程，Redis 还在

# 用户 B 完全隔离
print(chat("user_bob", "你好"))