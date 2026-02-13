class MockRecorder:

    def __init__(self):
        self.records = []

    def record(self, *args, **kwargs):
        self.records.append((args, kwargs))

    def get_records(self):
        return self.records
