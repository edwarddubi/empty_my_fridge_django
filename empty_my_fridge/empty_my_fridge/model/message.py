class Message:
    def __init__(self):
        self.message = None
        self.msg_type = None

    def get_message(self):
        return self.message

    def set_message(self, message):
        self.message = message

    def get_msg_type(self):
        return self.msg_type

    def set_msg_type(self, msg_type):
        self.msg_type = msg_type          