class MemoryMerger:

    def merge(
        self,
        old_value: str,
        new_value: str
    ) -> str:

        old_values = [
            value.strip()
            for value in str(old_value).split(",")
            if value.strip()
        ]

        new_values = [
            value.strip()
            for value in str(new_value).split(",")
            if value.strip()
        ]

        for value in new_values:

            if value.lower() not in [
                existing.lower()
                for existing in old_values
            ]:
                old_values.append(value)

        return ", ".join(old_values)