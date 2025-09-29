class Email:
    sender = None
    receiver = None
    cc = []
    bcc = []
    sent_timestamp = None
    received_timestamp = None
    subject = None

    def __init__(self, **kwargs):
        self.sender = kwargs.get("sender", "")
        self.receiver = kwargs.get("receiver", "")
        self.subject = kwargs.get("subject", "")
        self.cc = kwargs.get("cc", [])
        self.bcc = kwargs.get("bcc", [])
        self.sent_timestamp = kwargs.get("sent", None)
        self.received_timestamp = kwargs.get("received_timestamp", None)
        logger.debug(f"Initialized a new Email Instance: {self}")
    
    def __str__(self):
        return f"{{sender: {self.sender}, receiver: {self.receiver}, cc: {self.cc}, bcc: {self.bcc}, sent_timestamp: {self.sent_timestamp},  received_timestamp: {self.received_timestamp}}}"



