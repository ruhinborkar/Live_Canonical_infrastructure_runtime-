
import hashlib


class RuntimeHasher:

    @staticmethod
    def generate_hash(
        serialized_payload
    ):

        return hashlib.sha256(

            serialized_payload.encode()

        ).hexdigest()
