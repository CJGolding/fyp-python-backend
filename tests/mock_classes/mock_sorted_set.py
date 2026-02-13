class MockSortedSet:

    def __init__(self):
        self._data = []

    def add(self, item):
        if item not in self._data:
            self._data.append(item)
            self._data.sort()

    def remove(self, item):
        if item in self._data:
            self._data.remove(item)

    def index(self, item):
        try:
            return self._data.index(item)
        except ValueError:
            raise ValueError(f"{item} is not in list")

    def __contains__(self, item):
        return item in self._data

    def __len__(self):
        return len(self._data)

    def __getitem__(self, key):
        return self._data[key]

    def __repr__(self):
        return f"MockSortedSet({self._data})"
