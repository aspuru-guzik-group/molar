class MolarBackendError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        msg = (
            "The client got an unexpected answer from the backend:\n"
            f"{status_code}: {message}"
        )
        super().__init__(msg)
