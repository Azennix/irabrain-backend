from datetime import datetime, timezone


class MemoryReinforcement:

    def reinforce(self, memory):

        memory.access_count += 1

        memory.last_accessed = datetime.now(
            timezone.utc
        )

        return memory