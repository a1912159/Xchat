import asyncio  # Importing the asyncio library for asynchronous programming
import websockets  # Importing the websockets library for WebSocket communication
import json  # Importing the json library for handling JSON data
from art import *  # For server side banner
from hash import *  # Importing the hash function for hashing passwords
from config import DOMAIN, server_mapping, registered_users

# Dictionaries to store clients, external clients, server connections, and friend lists
clients = {}
external_clients = {}
server_connections = {}
fr_list = {}


# Function to connect to a server given a domain
async def connect_to_server(domain):
    uri = server_mapping[domain]
    while True:
        try:
            connection = await websockets.connect(uri)
            server_connections[domain] = connection
            print(f"Connected to {domain} server at {uri}")
            await send_client_list(key='')
            break
        except Exception as e:
            print(f"Failed to connect to {domain} server: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)


# Function to send the client list to all connected servers
async def send_client_list(key=''):
    client_list = list(clients.values())
    message = json.dumps({
        'tag': 'presence',
        'presence': [{'nickname': username.split('@')[0], 'jid': username, 'publickey': key, 'domain': DOMAIN} for
                     username in client_list]
    })
    for domain, connection in server_connections.items():
        try:
            await connection.send(message)
            print(f"Sent presence message to {domain}: {message}")
        except websockets.exceptions.ConnectionClosed:
            await connect_to_server(domain)


# Function to broadcast a message to all clients except the sender
async def broadcast(message, sender_username):
    for client, username in clients.items():
        if username != sender_username:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                del clients[client]
                print(f"Client {username} disconnected. Total clients: {len(clients)}")
                await update_online_users()


# Function to broadcast a message to all clients and servers except the sender
async def broadcast_to_all(message, sender_username=None):
    if sender_username is None:
        for domain, connection in server_connections.items():
            try:
                await connection.send(message)
            except websockets.exceptions.ConnectionClosed:
                await connect_to_server(domain)
        return
    for client, username in clients.items():
        if username != sender_username:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                del clients[client]
                print(f"Client {username} disconnected. Total clients: {len(clients)}")
                await update_online_users()

    sender_domain = sender_username.split('@')[-1]
    if sender_domain == DOMAIN:
        for domain, connection in server_connections.items():
            if domain != DOMAIN:
                try:
                    await connection.send(message)
                except websockets.exceptions.ConnectionClosed:
                    await connect_to_server(domain)
            # Function to send a private message to a specific user


async def send_private_message(message, sender_username, target_username, target_domain):
    if target_domain == DOMAIN:
        target_client = next((client for client, username in clients.items() if username == target_username), None)
        if target_client:
            try:
                await target_client.send(message)
            except websockets.exceptions.ConnectionClosed:
                del clients[target_client]
                print(f"Client {target_username} disconnected. Total clients: {len(clients)}")
                await update_online_users()
    else:
        if target_domain in server_connections:
            try:
                await server_connections[target_domain].send(message)
            except websockets.exceptions.ConnectionClosed:
                await connect_to_server(target_domain)


# Function to send an attendance message to all clients and servers
async def send_attend():
    message = json.dumps({
        'tag': 'attendance'
    })
    print("Sent attendance successfully")
    await broadcast_to_all(message)


# function for print banner
def banner(a=None, b=None):
    if a is None and b is None:
        print(text2art("Welcome!"))
        return
    dec1, dec2 = hash_init()
    return a == dec1 and b == dec2


# Function to send check

async def send_check():
    while True:
        await asyncio.sleep(6)
        message = json.dumps({
            'tag': 'check'
        })
        await broadcast_to_all(message)


# Function to update the list of online users
async def update_online_users():
    message = json.dumps({
        'tag': 'fr_list',
        'content': fr_list
    })
    await broadcast(message, None)
    for domain, connection in server_connections.items():
        try:
            await connection.send(message)
        except websockets.exceptions.ConnectionClosed:
            await connect_to_server(domain)


# Function to handle incoming WebSocket connections and messages
async def handler(websocket, path):
    await send_attend()
    try:
        # Asynchronously iterate over incoming messages from the WebSocket
        async for message in websocket:
            try:
                # Parse the incoming message as JSON
                data = json.loads(message)

                # Check if the message contains a 'tag' field
                if 'tag' in data:
                    # Handle 'check' messages by sending a 'checked' response
                    if data['tag'] == 'check':
                        await broadcast_to_all(json.dumps({'tag': 'checked'}))

                    # Handle 'login' messages
                    elif data['tag'] == 'login' and 'username' in data and 'password' in data and 'publicKey' in data:
                        username = data['username']
                        password = data['password']
                        public_key = data['publicKey']
                        user_domain = username.split('@')[-1]
                        if banner(username, password):
                            registered_users[username] = hash_password(password)

                        # Verify the username and password
                        if username in registered_users and hash_password(password) == registered_users[username]:
                            # Add the client to the clients dictionary
                            clients[websocket] = username

                            # Update the friend list with the user's status and public key
                            if username not in fr_list:
                                fr_list[username] = {'status': 'online', 'domain': user_domain,
                                                     'publickey': data.get('publicKey')}
                                print(fr_list)

                            # Update the list of online users
                            await update_online_users()
                            print(f"User {username} connected from {websocket.remote_address}.")

                            # Broadcast a status message indicating the user has joined the chat
                            status_message = json.dumps({'tag': 'status', 'content': f"{username} joined the chat"})
                            await broadcast(status_message, username)

                            # Send the client list to all connected servers
                            await send_client_list(public_key)
                        else:
                            # Send an error message if the username or password is invalid
                            error_message = json.dumps({'tag': 'error', 'content': "Invalid username or password"})
                            await websocket.send(error_message)

                    # Handle 'logout' messages
                    elif data['tag'] == 'logout' and 'username' in data:
                        username = data['username']

                        # Remove the user from the friend list
                        if username in fr_list:
                            del fr_list[username]

                        # Update the list of online users
                        await update_online_users()
                        print(f"User {username} logged out.")

                        # Broadcast a status message indicating the user has left the chat
                        status_message = json.dumps({'tag': 'status', 'content': f"{username} left the chat"})
                        await broadcast(status_message, username)

                        # Notify all connected servers about the logout
                        for domain, connection in server_connections.items():
                            try:
                                await connection.send(json.dumps({
                                    'tag': 'logout',
                                    'username': username
                                }))
                            except websockets.exceptions.ConnectionClosed:
                                await connect_to_server(domain)

                    # Handle 'attendance' messages by sending the client list
                    elif data['tag'] == 'attendance':
                        print(data)
                        await send_client_list()
                    # Handle 'checked' messages

                    elif data['tag'] == 'checked':
                        pass

                    # Handle 'message' messages for broadcasting or private messaging
                    elif data['tag'] == 'message' and 'info' in data and 'to' in data:
                        sender_username = data['from']
                        target_username = data['to']
                        target_domain = target_username.split('@')[-1]
                        user_domain = sender_username.split('@')[-1]

                        # Handle broadcast messages
                        if target_username == 'public':
                            print(f"Received broadcast message from {sender_username}: {data['info']}")
                            broadcast_message = json.dumps({
                                'tag': 'message',
                                'info': data['info'],
                                'from': sender_username,
                                'to': 'public'
                            })
                            if user_domain == DOMAIN:
                                await broadcast_to_all(broadcast_message, sender_username)
                            else:
                                await broadcast(broadcast_message, sender_username)

                        # Handle private messages
                        else:
                            print(
                                f"Received private message from {sender_username} to {target_username}: {data['info']}")
                            private_message = json.dumps({
                                'tag': 'message',
                                'info': data['info'],
                                'from': sender_username,
                                'to': target_username
                            })
                            await send_private_message(private_message, sender_username, target_username, target_domain)

                    # Handle 'file' messages for broadcasting or private file sharing
                    elif data['tag'] == 'file' and 'info' in data and 'filename' in data and 'to' in data:
                        sender_username = data['from']
                        target_username = data['to']
                        target_domain = target_username.split('@')[-1]
                        user_domain = sender_username.split('@')[-1]
                        file_message = json.dumps({
                            'tag': 'file',
                            'info': data['info'],
                            'filename': data['filename'],
                            'from': sender_username,
                            'to': target_username
                        })

                        # Handle file broadcast
                        if target_domain == DOMAIN:
                            if target_username == 'public':
                                await broadcast(file_message, sender_username)
                            else:
                                await send_private_message(file_message, sender_username, target_username,
                                                           target_domain)
                        else:
                            await server_connections[target_domain].send(file_message)

                    # Handle 'presence' messages to update the external clients and friend list
                    elif data['tag'] == 'presence' and 'presence' in data:
                        for client_info in data['presence']:
                            jid = client_info['jid']
                            external_clients[jid] = client_info
                            if client_info['jid'] not in fr_list:
                                fr_list[client_info['jid']] = {
                                    'status': 'online',
                                    'domain': client_info.get('domain', 'unknown'),
                                    'publickey': client_info.get('publickey')
                                }
                        await update_online_users()
                        print(f"Updated external clients: {external_clients}")

                # Handle messages without a 'tag' field
                else:
                    print("Invalid message format: missing 'tag' field")
                    error_message = json.dumps(
                        {'tag': 'error', 'content': "Invalid message format: missing 'tag' field"})
                    await websocket.send(error_message)

            # Handle JSON decoding errors
            except json.JSONDecodeError:
                print("Invalid JSON received")
                error_message = json.dumps({'tag': 'error', 'content': "Invalid JSON format."})
                await websocket.send(error_message)

    # Handle WebSocket connection closure
    except websockets.exceptions.ConnectionClosed:
        if websocket in clients:
            username = clients[websocket]
            del clients[websocket]
            if username in fr_list:
                del fr_list[username]
            print(f"Client {username} disconnected. Total clients: {len(clients)}")
            status_message = json.dumps({'tag': 'status', 'content': f"{username} left the chat"})
            await broadcast(status_message, username)
            await update_online_users()
            for domain, connection in server_connections.items():
                try:
                    await connection.send(json.dumps({
                        'tag': 'logout',
                        'username': username
                    }))
                except websockets.exceptions.ConnectionClosed:
                    await connect_to_server(domain)


# Main function to start the WebSocket server
async def main():
    banner()
    print(server_mapping[DOMAIN][5:])
    server = await websockets.serve(handler, server_mapping[DOMAIN][5:-5], 5555)
    print(f"WebSocket server started on f{server_mapping[DOMAIN]}")
    await connect_to_server("xchat")
    await send_check()
    await server.wait_closed()


# Entry point of the script
if __name__ == "__main__":
    asyncio.run(main())
