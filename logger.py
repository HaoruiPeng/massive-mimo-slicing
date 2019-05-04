class Logger:
    def __init__(self, file_name):
        self.file = open(file_name, 'w')

    def write(self, message):
        self.file.write(message)

    def close(self):
        self.file.close()
