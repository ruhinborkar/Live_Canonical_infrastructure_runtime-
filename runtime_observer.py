
class RuntimeObserver:

    @staticmethod
    def observe(
        stage,
        status
    ):

        print(
            f"[OBSERVABILITY] STAGE={stage} | STATUS={status}"
        )
