class AssociationBuilder:

    def build(self, memory):

        return (
            f"category: {memory.category} "
            f"key: {memory.key} "
            f"value: {memory.value}"
        ).strip()