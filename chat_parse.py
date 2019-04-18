







class Participant:
    """
    docstring
    """

    def __init__(self, name: str):
        self.name_in_chat = name


class Message:
    """
    docstring
    """

    def __init__(self, datetime: datetime, sender: Participant, orig_text: str, chat: Chat, msg_number: int):
        self.datetime = datetime
        self.sender = sender
        self.orig_text = orig_text
        self.chat = chat
        self.msg_number = msg_number
        self.ID = self.chat.ID + self.msg_number
        self.sensored_text = None
        self.attachments = None


class Chat:
    """
    docstring
    """

    def __init__(self, chatID:str, meta_:str = None):
        self.messages = []
        self.participants = set()
        self.ID = chatID
        self.meta = meta_

    def add_msg(self, msg: Message):
        pass

    def add_participant(self, participant: Participant):
        pass

    def anonymize(self):
        pass

    def replace_word(self, string_to_replace: str, replace_with: str):
        pass
    
    def find_all_links(self):
        pass     

    def find_all_phones(self):
        pass   

    def to_csv(self, filename: str):
        pass
    
    def to_json(self, filename: str):
        pass





def parse_chat(chat_str: str, delimiter_format: str):
    """
    """
    chat = Chat()

    msg_strs = split_with_delimiter(chat_str, delimiter_format)
    
    for msg_str in msg_strs:
        msg = parse_msg(msg_str, delimiter_format)
        
        chat.add_msg(msg)
        chat.add_participant(msg.sender)

    return chat 


def split_with_delimiter(chat_str: str, delimiter_format: str):
    return 

def parse_msg(msg_str: str, delimiter_format: str):
    return 

