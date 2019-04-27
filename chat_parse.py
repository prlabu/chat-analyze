import re
from datetime import datetime 
from dateutil.parser import parse as dt_parse
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
        self.participants.add(participant)
        return

    def get_participant_by_name(self, part_name):
        for part in self.participants:
            if part.name_in_chat ==  part_name:
                return part
        
        print(f'No participant found by name: {part_name}')
        return

    def user_add_participant_info(self):
        for 

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
        self.ID = self.chat.ID + str(self.msg_number)
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


    split_on = re.sub(r'\w+', r'.+', delimiter_format[:-1])
    split_on = re.sub(r'([\[\]])', r'\\\1', split_on)

    msg_strs = split_on(chat_str, split_on)
    
    for i, msg_str in enumerate(msg_strs):
        msg = parse_msg(msg_str, delimiter_format, chat=chat, msg_number=i)
        
        chat.add_msg(msg)

    return chat 


def split_on(split_on_re: str, chat_str: str):
    """ Splits a string according to a regex pattern.

    Arguments:

    Returns:
    """

    msg_strs = re.split(f'\s(?={split_on_re})', chat_str)

    # eliminate empty strings from the list
    msg_strs = [msg_str for msg_str in msg_strs if msg_str.strip()]

    return msg_strs


def parse_msg(msg_str: str, delimiter_format: str, chat:Chat, msg_number:int):
    """ Parses a single message string into a message object.

    Arguments:

    Returns:
    """


    msg_re = re.sub(r'(\w+)', r'(?P<\1>.*)', delimiter_format)
    msg_re = re.sub(r'([\[\]])', r'\\\1', msg_re)
    msg_re = msg_re + '(?P<msg>.*)'

    msg_mtch = re.match(msg_re, msg_str, re.DOTALL)
    if not msg_mtch:
        print('Error in parsing msg: \n     msg_str')
        return None

    date = msg_mtch.group('date').strip()
    time = msg_mtch.group('time').strip()
    datetime_obj = parse_datetime(date + ' ' + time)

    sender_name = msg_mtch.group('sender').strip()
    if sender_name not in list(map(lambda part: part.name_in_chat, chat.participants)):
        new_part = Participant(sender_name)
        chat.add_participant(new_part)
        sender = new_part
    else:
        sender = chat.get_participant_by_name(sender_name)

    text = msg_mtch.group('msg').strip()

    msg_obj = Message(datetime_obj, sender, text, chat=chat, msg_number=msg_number)
    return msg_obj


def parse_datetime(datetime_str: str):
    """ Attempts to parse the a date-time string.

    Arguments:

    Returns:
    """

    # using dateutil.parser.parse
    return dt_parse(datetime_str)



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
    
    ip = input('Would you like to add participant information?')
    if ip.lower() in ['y', 'yes']:
        chat.user_add_participant_info()

    return


def test_parse_msg():
    delimiter_format = '[date, time] sender:'
    msg_str = '[1/28/19, 16:07:03] Latané Bullock: come all ye little ones'
    chat = Chat('myChat')
    msg_obj = parse_msg(msg_str, delimiter_format, chat, 1)
    return msg_obj



if __name__ == "__main__":
    # main()
    test_parse_msg()

    
