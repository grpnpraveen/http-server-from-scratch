import sys
import gzip
import socket
import threading

def handle_client(client_socket, client_address):
    print(f"[INFO] client address: {client_address}\n")
    while True:
        data=None
        client_socket.settimeout(5.0)  # Timeout after 5 seconds
        try:
            data = client_socket.recv(1024).decode()
        except socket.timeout:
            print("Socket timed out, no data received.")
        if not data:
            break
        handle_client_request(client_socket, data)

    client_socket.send(b"HTTP/1.1 200 OK\r\n\r\n")

def handle_client_request(client_socket, request):
    print(f"[INFO] client request: {request}\n")
    # Split the resquest into lines
    lines = request.split("\r\n")
    command, path, _ = lines[0].split(" ")
    print(f"[INFO] client method: {command}\n")
    print(f"[INFO] client requested path: {path}\n")
    if command.upper() == "GET":
        if path=="/user-agent":
            user_agent_line = None
            for each_line in lines:
                if each_line.lower().startswith("user-agent"):
                    user_agent_line = each_line 
            client_socket.send(get(path,{"user-agent":user_agent_line[12:]}).encode())
        else:
            accept_encoding_line = None
            for each_line in lines:
                if each_line.lower().startswith("accept-encoding"):
                    accept_encoding_line = each_line
            if accept_encoding_line is not None: 
                client_socket.send(get(path,values={"accept-encoding":accept_encoding_line[17:]})) 
            else:
                client_socket.send(get(path).encode())
    elif command.upper() == "POST":
        if path[:6] == "/files":
            client_socket.send(post(path,{"file-content":lines[-1]}).encode())

# POST METHOD
def post(path,values=None):
    if path[:6] == "/files":
        directory = sys.argv[2]
        print(f"[INFO] {directory}/{path[7:]}\n")
        f = open(f"/{directory}/{path[7:]}", "a")
        f.write(values["file-content"])
        f.close()
        return send_response(201)

# GET METHOD
def get(path,values=None):
    if path == "/":
        return send_response(200)
    elif path=="/user-agent":
        return send_response("user-agent",values["user-agent"])
    elif path[:5]=="/echo":
        return send_response("echo",path[6:],extra_data=values)
    elif path[:6]=="/files":
        directory = sys.argv[2]
        print(f"[INFO] {directory}/{path[7:]}\n")
        f=None
        try:
            f = open(f"/{directory}/{path[7:]}", "r")
        except:
            return send_response(404)
        file_content = f.read() 
        f.close()
        return send_response("files",response=file_content)
    else:
        return send_response(404)
    

def send_response(response_code,response=None,extra_data=None):
    if response_code == 404:
        return "HTTP/1.1 404 Not Found\r\n\r\n"
    elif response_code == 200:
        return "HTTP/1.1 200 OK\r\n\r\n"
    elif response_code == 201:
        return "HTTP/1.1 201 Created\r\n\r\n"
    elif response_code=="echo" or response_code=="user-agent" or response_code=="files":
        content_type = "text/plain"
        if response_code=="files":
            content_type = "application/octet-stream"
        if extra_data is not None:
            if extra_data["accept-encoding"] is not None:
                if "gzip" in extra_data["accept-encoding"].split(", "):
                    print("RRR")
                    print(response)
                    print(len(response))
                    # byte_data = response.encode()
                    # compressed_data = gzip.compress(byte_data)
                    # print(compressed_data)
                    compressed_val = gzip.compress(str.encode(response))
                    return f"HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\nContent-Type: text/plain\r\nContent-Length: {len(compressed_val)}\r\n\r\n".encode() + compressed_val
                    # return f"HTTP/1.1 200 OK\r\nContent-Encoding: gzip\r\nContent-Type: {content_type}\r\nContent-Length: {len(compressed_data)}\r\n\r\n{compressed_data}\r\n\r\n"  
                else:
                    return f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {len(response)}\r\n\r\n{response}\r\n\r\n".encode()


        return f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {len(response)}\r\n\r\n{response}\r\n\r\n"

    
def main():
    print("Server Started!\n")
    server_socket = socket.create_server(("localhost", 4221), reuse_port=False)
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            thread1 =threading.Thread(target=handle_client, args=(client_socket, client_address))
            thread1.start()
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt")
    finally:
        server_socket.close()
        print("\nServer Closed")


if __name__ == "__main__":
    main()
