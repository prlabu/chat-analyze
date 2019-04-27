import re
from datetime import datetime 
import dateutil
import sys
import os


class Participant:
    """
    docstring
    """

    def __init__(self, name: str):
        self.name_in_chat = name


class Chat:
    """
    docstring
    """

    def __init__(self, chatID:str, meta_:str = None):
        self.messages = []
        self.participants = set()
        self.ID = chatID
        self.meta = meta_

    def add_msg(self, msg):
        pass

    def add_participant(self, participant:Participant):
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

    def from_json(self, filename: str):
        pass


class Message:
    """
    docstring
    """

    def __init__(self, datetime: datetime, sender: Participant, orig_text: str, chat: Chat, msg_number:int):
        self.datetime = datetime
        self.sender = sender
        self.orig_text = orig_text
        self.chat = chat
        self.msg_number = msg_number
        self.ID = self.chat.ID + self.msg_number
        self.sensored_text = None
        self.attachments = None
        self.type = None




def parse_chat(chat_name:str, chat_str:str, delimiter_format:str):
    """ Takes an exported WhatsApp chat (.txt) and creates a chat object with messages.

    Arguments:
    chatName -- string identifying the name of the chat 
    chat_str -- full string containing the exported WhatsApp chat
    delimiter_format -- format the WhatsApp-generated delimiter. Essentially the 
        header of each message in the .txt file. 

    """

    chat = Chat(chat_name, 'No metadata provided')

    split_on = re.sub(r'\w+', r'.+', delimiter_format)
    split_on = re.sub(r'([\[\]])', r'\\\1', split_on)
    msg_strs = split_on(chat_str, split_on)
    
    for i, msg_str in enumerate(msg_strs):
        msg = parse_msg(msg_str, delimiter_format, chat=chat, msg_number=i)
        
        chat.add_msg(msg)
        chat.add_participant(msg.sender)

    return chat 


def split_on(chat_str: str, split_on_re: str):
    """ Splits a string according to a regex pattern.

    Arguments:

    Returns:
    """

    msg_strs = re.split(f'\s(?={split_on_re})', chat_str)

    # eliminate empty strings from the list
    msg_strs = [msg_str for msg_str in msg_strs if msg_str.strip()]

    return msg_strs


def parse_msg(msg_str: str, header_format_re: str, chat:Chat, msg_number:int):
    """ Parses a single message string into a message object.

    Arguments:

    Returns:
    """

    msg_mtch = re.match(header_format_re, msg_str)
    if not msg_mtch:
        return None
    
    datetime_obj = parse_datetime(msg_mtch.group('datetime'))
    sender = msg_mtch.group('sender')
    text = msg_mtch.group('msg-content')

    return Message(datetime_obj, sender, text, chat=chat, msg_number=msg_number)


def parse_datetime(datetime_str: str):
    """ Attempts to parse the a date-time string.

    Arguments:

    Returns:
    """

    return dateutil.parser.parse(datetime_str)



def main():
    try: 
        dummy, chat_txt_file, op_file, delim_re = sys.argv
    except: 
        print('Couldn\'t understand inputs')
        print('The usage is chat_parse.py <input-text-file> <output-csv-file>')

    f = open(chat_txt_file, 'r')
    chat_str = f.read()
    f.close()
    
    chat_name = os.path.splitext(os.path.basename(chat_txt_file))[0]
    chat = parse_chat(chat_name, chat_str, '')
    
    return




if __name__ == "__main__":
    main()

    
