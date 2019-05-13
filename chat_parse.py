import re
from datetime import datetime 
from dateutil.parser import parse as dt_parse
import sys
import os
from enum import Enum
import csv
import phonenumbers
import json

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
        self.pseudonym = name
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

    def __init__(self, chatID:str, format_:dict,meta_:str = None):
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

    def user_add_participants_info(self):
        for part in self.participants:
            ip = input(f'Would you like to add info for participant name: "{part.name_in_chat}" ? (y/n, q to quit) \n')
            if ip.lower() in ['y', 'yes']:
                part.user_add_details()
            elif ip.lower() in ['q', 'quit']:
                break
        return

    def to_messages_csv(self):
        msgs_outfile = f'assets/{self.ID}-msgs.csv'

        msg_f = open(msgs_outfile, 'w')
        fieldnames = ['chatID', 'datetime', 'sender', 'sensored_text']
        writer = csv.DictWriter(msg_f, dialect='excel', fieldnames=fieldnames)
        writer.writeheader()

        for msg in self.messages:
            msg_dic = {}
            msg_dic['chatID'] = self.ID
            msg_dic['datetime'] = str(msg.datetime)
            msg_dic['sender'] = str(msg.sender.pseudonym)
            msg_dic['sensored_text'] = str(msg.sensored_text)

            msg_dic = {k:v for k,v in msg_dic.items() if k in fieldnames}
            
            writer.writerow(msg_dic)
        msg_f.close()

        return

    def anonymize(self):
        pass

    def replace_word(self, string_to_replace: str, replace_with: str):
        pass
    
    def find_all_links(self):
        web_link_re = re.compile(r'https?://[\S]+')
        for msg in self.messages:
            msg.sensored_text = web_link_re.sub('<web link omitted>', msg.sensored_text)
        return     

    def find_all_phones(self):
        # phone_re = re.compile(r'\+?[0-9][0-9 ()-]{7,13}[0-9]')
        phone_re = re.compile(r'@[0-9]{10,12}')
        for msg in self.messages:
            mtches = phone_re.findall(msg.sensored_text)
            for mtch in mtches:
                ip = input(f'Would you like to replace "{mtch}" in the following message? (y/n)\n {msg.sensored_text}\n')
                if is_user_ip_true(ip):
                    msg.sensored_text = re.sub(re.escape(mtch), '<phone number omitted>', msg.sensored_text)
        return

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
        self.sensored_text = orig_text
        self.chat = chat
        self.msg_number = msg_number
        self.ID = self.chat.ID + str(self.msg_number)
        self.attachments = None
        self.type = None


def is_user_ip_true(ip: str):
    ip = ip.lower()
    return ip in ['y', 'yes']


def parse_chat(chat_name:str, chat_str:str, chat_format:str):
    """ Takes an exported WhatsApp chat (.txt) and creates a chat object with messages.

    Arguments:
    chatName -- string identifying the name of the chat 
    chat_str -- full string containing the exported WhatsApp chat
    chat_format -- format the WhatsApp-generated delimiter. Essentially the 
        header of each message in the .txt file. Eg: "[dateDMY, time24] sender: content"

    """

    chat = Chat(chatID=chat_name, format_=chat_format, meta_='No metadata provided')

    # split_on_re = chat.format.split('sender')[0]   # get everything up until 'sender'
    # split_on_re = re.sub(r'([\[\]])', r'\\\1', split_on_re) # escape brackets if they exist
    # split_on_re = re.sub(r'\w+', r'.+', split_on_re)
    split_on_re = chat.format['split_on_re']

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
    print(f'Split_on re: "{split_on_re}"')

    # eliminate empty strings from the list
    msg_strs = [msg_str for msg_str in msg_strs if msg_str.strip()]

    return msg_strs


def parse_msg(msg_str: str, chat:Chat, msg_number:int):
    """ Parses a single message string into a message object.

    Arguments:

    Returns:
    """


    # msg_re = re.sub(r'(\w+)', r'(?P<\1>.*)', chat.format)
    # msg_re = re.sub(r'([\[\]])', r'\\\1', msg_re)
    msg_re = chat.format['std_msg_re']

    msg_mtch = re.match(msg_re, msg_str, re.DOTALL)
    if not msg_mtch:
        # note a std message type - see if the message is sent by WhatsApp

        WA_re = chat.format['WA_msg_re']
        # WA_re += '(?P<remain>.*)' # the msg format is then something like '[date, time] whats-app-messge'
        
        WA_mtch = re.match(WA_re, msg_str, re.DOTALL)
        
        # if not the format of a normal message and not a WhatsApp meta message .... 
        if not WA_mtch:
            print(f'Error in parsing msg: \n     "{msg_str}"')
            # print(f'Regex used: {WA_re}\n')
            return None

        date = WA_mtch.group('date').strip()
        time = WA_mtch.group('time').strip()
        datetime_obj = parse_datetime(date + ' ' + time)
        sender_name = 'WhatsApp'
        sender = chat.add_participant_by_name(sender_name)
        text = WA_mtch.group('remain').strip()
        

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

    # ip = input('What is the name (directory+filename) of the chat.txt? \n')
    # chat_txt_file = ip
    # comeagain = not os.path.exists(ip)
    # while comeagain:
    #     print('Coundn\'t find a directory by that name.')
    #     ip = input('What is the name (directory+filename) of the chat.txt? (q to quit) \n')
    #     if ip in ['q', 'quit']:
    #         return
    #     if os.path.exists(ip):
    #         comeagain = False
    #         chat_txt_file = ip
        
    # ip_prompt = 'What is the delimiter format of the text?\n '
    # ip_prompt += 'Eg: "[date, time] sender: content" ... Please refer to the README for more info \n'
    # ip = input(ip_prompt)
    # delim_format = ip

    # chat_txt_file = 'assets/test2.txt'
    chat_txt_file = 'assets/3-2018-CHI_F59_R_x.txt'
    # delim_format = 'date, time - sender: content'
    chat_name = os.path.splitext(os.path.basename(chat_txt_file))[0]
    
    with open('assets/' + chat_name + '-format.json', 'r') as f:
        format_ = json.loads(f.read())

    f = open(chat_txt_file, 'r', encoding='utf-8-sig')
    chat_str = f.read()
    f.close()
    
    chat = parse_chat(chat_name, chat_str, format_)
    
    ip = input('Would you like to add participant information? (y/n)\n')
    if is_user_ip_true(ip):
        chat.user_add_participants_info()
    
    ip = input('Would you like to find and replace all web links? (y/n) \n')
    if is_user_ip_true(ip):
        chat.find_all_links()

    ip = input('Would you like to find all phone numbers? (y/n) \n')
    if is_user_ip_true(ip):
        chat.find_all_phones()

    ip = input('Would you like to output the messages to a CSV? (y/n) \n')
    if is_user_ip_true(ip):
        chat.to_messages_csv()

    return


def test_parse_msg():
    delimiter_format = '[date, time] sender: content'
    msg_str = '[1/28/19, 16:07:03] Latané Bullock: come all ye good ones'
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
    main()

    # test_parse_msg()

    # test_participant()

    # test_chat_to_messages_csv()