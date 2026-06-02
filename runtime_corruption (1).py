
class RuntimeCorruption:

    @staticmethod
    def inject_sequence_corruption(
        payload
    ):

        payload["sequence_id"] = 999

        return payload
