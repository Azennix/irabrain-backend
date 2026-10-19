from brain.engine.engine import Engine


class MemoryEngine(Engine):

    def __init__(
        self,
        memory_service
    ):
        self.memory_service = memory_service

    def execute(
        self,
        request
    ):

        print(
            "\n========== MEMORY ENGINE EXECUTE =========="
        )

        print(
            "MemoryEngine received request"
        )

        print(
            "User ID :",
            request.user_id
        )

        print(
            "Query   :",
            request.query
        )

        print(
            "==========================================="
        )

        workspace_mode = request.metadata.get(
            "workspace_mode",
            "personal"
)

        if workspace_mode == "private":

            print(
                "[PRIVATE SPACE] Memory write skipped"
    )

            return None

        result = self.memory_service.store(
            request
)

        print(
            "\n========== MEMORY SERVICE COMPLETE =========="
        )

        print(
            "MemoryService.store() finished"
        )

        print(
            "============================================="
        )

        return result