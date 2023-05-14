import socket
import os
import json
from telethon import TelegramClient
from config import TG_API_HASH, TG_API_ID, TG_BOT_TOKEN, TG_DEFAULT_CHAT, SOCKET_PATH

tgClient = None


async def server():
    global tgClient

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        os.remove(SOCKET_PATH)
    except OSError:
        pass
    s.bind(SOCKET_PATH)
    s.listen()

    print('Server is up')

    while True:
        conn, addr = s.accept()
        try:
            datalen = int(conn.recv(8).decode('utf8'))
            data = b''
            while len(data) < datalen:
                tmp = conn.recv(1024)
                if not tmp:
                    break
                data += tmp
            data = json.loads(data.decode('utf8'))
            print(data)

            if data['action'] == 'send':
                res = await tgClient.send_message(
                    int(data['chat_id']),
                    data['message'],
                    parse_mode='html',
                    link_preview=False,
                )
                result = {
                    'message_id': res.id,
                }
            elif data['action'] == 'edit':
                res = await tgClient.edit_message(
                    int(data['chat_id']),
                    int(data['message_id']),
                    data['message'],
                    parse_mode='html',
                    link_preview=False,
                )
                result = {
                    'message_id': res.id,
                }

            result = json.dumps(result).encode('utf8')

            conn.sendall('{:08d}'.format(len(result)).encode('utf8'))
            conn.sendall(result)
        except Exception as e:
            print(e)

        conn.close()


def main():
    tgClient = TelegramClient(None, TG_API_ID, TG_API_HASH).start(bot_token=TG_BOT_TOKEN)
    tgClient.loop.run_until_complete(server())


if __name__ == '__main__':
    main()
