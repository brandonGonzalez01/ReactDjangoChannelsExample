# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
'''
Things to do:
add voting receiving and broadcasting function for elimination
'''
class GameConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        print('connecting! ', self.scope)
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        
        self.room_group_name = 'chat_%s' % self.room_name
        self.username = ''
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print('accepted connection')
        
    async def disconnect(self, close_code):
        print('self: ',self.username)
        print(close_code)   
        await self.channel_layer.group_send(
            #broadcast that you have left
            self.room_group_name,
            {
                'type': 'leaving',
                'message': self.username,
            }
            )
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket(from client)
    async def receive(self, *, text_data):
        text_data_json = json.loads(text_data)
        print('received websocket mssg: ',text_data_json)
        #command is a key whose value will be a function(), this is just so that receive function isnt too big
        await self.commands[text_data_json['command']](self, text_data_json)

    #recieve message that player has disconnected
    async def leaving(self, event):
        message = event['message']
        print(f'ln51: user leaving: {message}')
        
        #send message to pyrebase that self.username is leaving
        print('pyrebase do something')
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'command': 'leaving',
            'user': message
        }))

    #broadcast that new player joined
    async def joining(self, event):
        print('new user joining game')
        username = event['username']
        print('user joining: ',username)
        #send to group(broadcast)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'new_user',
                'username': username
            }   
        )

    async def set_user(self, event):
        print(f'setting user name! {event}')
        self.username = event['username']

    #receive new user from group(joining() was broadcasted)
    async def new_user(self, event):
        username = event['username']
        print(f'new user recvd: {username}')
        # Send username to WebSocket
        await self.send(text_data=json.dumps({
            'command': 'new_user',
            'username': username
        }))

    # Receive message from room group
    async def chat_message(self, event):
        print('recieving mssg!')
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    #key-values so receiveing function knows what to do
    commands = {
        'new_message': chat_message,
        'leaving': leaving,
        'joining': joining,
        'set_user': set_user,
    }
