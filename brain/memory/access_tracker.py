from datetime import datetime, timezone

class MemoryAccessTracker:

    def __init__(self, repository):
        self.repository = repository

    def track(self, memories):

        print("\n===== ACCESS TRACKER =====")

        for memory in memories:

            print("Before:", memory.key, memory.access_count)

            memory.access_count += 1
            memory.last_accessed = datetime.now(timezone.utc)

            self.repository.update_access(memory)

            print("After :", memory.key, memory.access_count)

        print("==========================\n")

        return memories