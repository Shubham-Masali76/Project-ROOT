class GenerateContentConfig:
    def __init__(self, response_mime_type=None, temperature=None):
        self.response_mime_type = response_mime_type
        self.temperature = temperature

class PartMock:
    def __init__(self, data, mime_type):
        self.data = data
        self.mime_type = mime_type

class Part:
    @staticmethod
    def from_bytes(data, mime_type):
        return PartMock(data, mime_type)
