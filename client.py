import argparse
import json
import os
import socket

from config import TG_API_HASH, TG_API_ID, TG_BOT_TOKEN, TG_DEFAULT_CHAT, SOCKET_PATH
from telethon import TelegramClient


def client(action, message, message_id=0, chat_id=TG_DEFAULT_CHAT):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(SOCKET_PATH)
    req = json.dumps({
        'action': action,
        'message': message,
        'chat_id': chat_id,
        'message_id': str(message_id),
    }).encode('utf8')
    s.sendall('{:08d}'.format(len(req)).encode('utf8'))
    s.sendall(req)
    datalen = int(s.recv(8).decode('utf8'))
    data = b''
    while len(data) < datalen:
        tmp = s.recv(1024)
        if not tmp:
            break
        data += tmp
    data = json.loads(data.decode('utf8'))
    s.close()
    return data


def send_tg_message(message, chat_id=TG_DEFAULT_CHAT):
    return client('send', message, chat_id=chat_id)


def edit_tg_message(message_id, message, chat_id=TG_DEFAULT_CHAT):
    return client('edit', message, message_id=message_id, chat_id=chat_id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='action')

    parser_send = subparsers.add_parser('send')
    parser_send.add_argument('message')
    parser_send.add_argument('--chat_id', default=TG_DEFAULT_CHAT, type=int)

    parser_edit = subparsers.add_parser('edit')
    parser_edit.add_argument('message_id', type=int)
    parser_edit.add_argument('message')
    parser_edit.add_argument('--chat_id', default=TG_DEFAULT_CHAT, type=int)

    args = parser.parse_args()

    if args.action == 'send':
        data = send_tg_message(args.message, args.chat_id)
        print(data)
    elif args.action == 'edit':
        data = edit_tg_message(args.message_id, args.message, args.chat_id)
        print(data)
    else:
        parser.print_help()
