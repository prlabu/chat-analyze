import re
from datetime import datetime 
from dateutil.parser import parse as dt_parse
import sys
import os
from enum import Enum
import csv

class MessageType(Enum):
    TEXT = 'text'
    WHATSAPP = 'whatsapp-meta'
    MEDIA =  'media'


class Participant:
    """
    docstring
    """

    def __init__(self, name: str):
        self.name_in_chat = name
        self.age = None
        self.pseudonym = None
        self.phone = None
        self.gender = None
        self.ethnicity = None

    def __str__(self):
        p_str = self.name_in_chat + '\n'
        for var, val in vars(self).items():
            if not var == 'name_in_chat':
                p_str += f'  {var}: {val}\n'
        return p_str

    def user_add_details(self):
        print('Current participant...')
        print(self)
        ip = input('Would you like to update any participant details? (y/n) \n')
        comeagain = is_user_ip_true(ip)

        while comeagain:
            detail = input(f'Which detail would you like to update for {self.name_in_chat}? ("age" or "gender", etc) \n')
            if hasattr(self, detail):
                val = input(f'What would you like {self.name_in_chat}\'s {detail} to be? \n')
                setattr(self, detail, val)
                print('Updated partcipant... ')
                print(self)
                print()

                ip = input(f'Would you like to enter more details? (y/n) \n\n')
                comeagain = is_user_ip_true(ip)
            else:
                print('Oops, Couldn\'t find that detail for the user.')
                ip = input(f'Would you try again? (y/n) \n\n')
                comeagain = is_user_ip_true(ip)
        
        return 


class Chat:
    """
    docstring
    """

    def __init__(self, chatID:str, format_:str,meta_:str = None):
        self.messages = []
        self.participants = set()
        self.ID = chatID
        self.meta = meta_
        self.format = format_

    def add_msg(self, msg):
        self.messages.append(msg)
        return

    def add_participant(self, participant:Participant):
        self.participants.add(participant)
        return

    def get_participant_by_name(self, part_name):
        for part in self.participants:
            if part.name_in_chat ==  part_name:
                return part
        
        print(f'No participant found by name: {part_name}')
        return

    def add_participant_by_name(self, part_name):
        """Always returns a participant - whether new or pre-existing
        """
        if part_name not in list(map(lambda part: part.name_in_chat, self.participants)):
            new_part = Participant(part_name)
            self.add_participant(new_part)
            part = new_part
        else:
            part = self.get_participant_by_name(part_name)
        return part

    def user_add_participant_info(self):
        pass

    def to_messages_csv(self):
        msgs_outfile = f'assets/{self.ID}-msgs.csv'

        msg_f = open(msgs_outfile, 'w')
        fieldnames = ['chatID', 'datetime', 'sender', 'orig_text']
        writer = csv.DictWriter(msg_f, dialect='excel', fieldnames=fieldnames)
        writer.writeheader()

        for msg in self.messages:
            msg_dic = {}
            msg_dic['chatID'] = self.ID
            msg_dic['datetime'] = str(msg.datetime)
            msg_dic['sender'] = str(msg.sender.name_in_chat)
            msg_dic['orig_text'] = str(msg.orig_text)

            msg_dic = {k:v for k,v in msg_dic.items() if k in fieldnames}
            
            writer.writerow(msg_dic)
        msg_f.close()

        return

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
        self.sensored_text = None
        self.chat = chat
        self.msg_number = msg_number
        self.ID = self.chat.ID + str(self.msg_number)
        self.attachments = None
        self.type = None


def is_user_ip_true(ip: str):
    ip = ip.lower()
    return ip == 'y' or ip == 'yes'


def parse_chat(chat_name:str, chat_str:str, chat_format:str):
    """ Takes an exported WhatsApp chat (.txt) and creates a chat object with messages.

    Arguments:
    chatName -- string identifying the name of the chat 
    chat_str -- full string containing the exported WhatsApp chat
    chat_format -- format the WhatsApp-generated delimiter. Essentially the 
        header of each message in the .txt file. Eg: "[dateDMY, time24] sender: content"

    """

    chat = Chat(chatID=chat_name, format_=chat_format, meta_='No metadata provided')

    split_on_re = chat.format.split('sender')[0]   # get everything up until 'sender'
    split_on_re = re.sub(r'\w+', r'.+', split_on_re)
    split_on_re = re.sub(r'([\[\]])', r'\\\1', split_on_re)

    msg_strs = split_on(split_on_re, chat_str)
    print(f'Chat split into -{len(msg_strs)}- messages')
    
    for i, msg_str in enumerate(msg_strs):
        msg = parse_msg(msg_str, chat=chat, msg_number=i)
        if msg:
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


def parse_msg(msg_str: str, chat:Chat, msg_number:int):
    """ Parses a single message string into a message object.

    Arguments:

    Returns:
    """


    msg_re = re.sub(r'(\w+)', r'(?P<\1>.*)', chat.format)
    msg_re = re.sub(r'([\[\]])', r'\\\1', msg_re)

    msg_mtch = re.match(msg_re, msg_str, re.DOTALL)
    if not msg_mtch:
    
        # see if the message is sent by WhatsApp
        WA_re = chat.format.split('sender')[0].strip()   # get everything up until 'sender'
        WA_re = re.sub(r'(\w+)', r'(?P<\1>.*)', WA_re)
        WA_re = re.sub(r'([\[\]])', r'\\\1', WA_re)
        WA_re += '(?P<remain>.*)'
        
        WA_mtch = re.match(WA_re, msg_str, re.DOTALL)
        if not WA_mtch:
            print(f'Error in parsing msg: \n     {msg_str}')
            return None

        date = WA_mtch.group('date').strip()
        time = WA_mtch.group('time').strip()
        datetime_obj = parse_datetime(date + ' ' + time)
        sender_name = 'WhatsApp'
        text = WA_mtch.group('remain').strip()
        sender = chat.add_participant_by_name(sender_name)

        msg_obj = Message(datetime_obj, sender=sender, orig_text=text, chat=chat, msg_number=msg_number)
        msg_obj.type = 'whatsapp-meta'


        return msg_obj

    date = msg_mtch.group('date').strip()
    time = msg_mtch.group('time').strip()
    datetime_obj = parse_datetime(date + ' ' + time)

    sender_name = msg_mtch.group('sender').strip()
    sender = chat.add_participant_by_name(sender_name)

    text = msg_mtch.group('content').strip()

    msg_obj = Message(datetime_obj, sender=sender, orig_text=text, chat=chat, msg_number=msg_number)
    msg_obj.type = 'user-text'
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
    delimiter_format = '[date, time] sender: content'
    msg_str = '[1/28/19, 16:07:03] Latané Bullock: come all ye little ones'
    chat = Chat(chatID='myChat', format_=delimiter_format)
    msg_obj = parse_msg(msg_str, chat, 1)
    return msg_obj

def test_participant():
    new_part = Participant(name='Bobby')
    new_part.user_add_details()

    return 

def test_chat_to_messages_csv():
    chat_txt_file = 'assets/ligma-export-trunk.txt'
    f = open(chat_txt_file, 'r')
    chat_str = f.read()
    f.close()
    
    chat_name = os.path.splitext(os.path.basename(chat_txt_file))[0]
    chat = parse_chat(chat_name, chat_str, '[date, time] sender: content')

    chat.to_messages_csv()

    return

if __name__ == "__main__":
    # main()

    # test_parse_msg()

    # test_participant()

    test_chat_to_messages_csv()