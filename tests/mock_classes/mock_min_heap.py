class MockMinHeap:

    def __init__(self):
        self._heap = []

    def push(self, item):
        self._heap.append(item)
        self._heap.sort()

    def pop(self):
        if self._heap:
            return self._heap.pop(0)
        return None

    def peek(self):
        if self._heap:
            return self._heap[0]
        return None

    def remove(self, item):
        if item in self._heap:
            self._heap.remove(item)

    def __contains__(self, item):
        return item in self._heap

    def __len__(self):
        return len(self._heap)

    def __repr__(self):
        return f"MockMinHeap({self._heap})"
