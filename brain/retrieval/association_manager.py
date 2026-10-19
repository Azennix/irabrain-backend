from brain.retrieval.association_builder import AssociationBuilder


class AssociationManager:

    def __init__(self):

        self.builder = AssociationBuilder()

    def build_for_memories(
        self,
        memories
    ):

        memory_associations = {}

        for memory in memories:

            text = self.builder.build(memory)
            print(
            "ASSOCIATION TEXT:",
             memory.key,
              "->",
              text
)



            memory_associations[
                memory.memory_id
            ] = {
                "text": text,
                "embedding": memory.association_embedding
            }

        return memory_associations