class ErrorHandler:
    def __init__(self):
        self.errors = {}
    def set_error(self, key, message):
        self.errors[key] = message
    def clear_error(self, key):
        self.errors.pop(key, None)
    def has_errors(self):
        return len(self.errors) > 0
    def get_all(self):
        return list(self.errors.values())
