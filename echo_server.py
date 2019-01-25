import socket
import sys
import traceback
import select
import queue as Queue

def server(log_buffer=sys.stderr):
    # set an address for our server
    address = ('127.0.0.1', 10003)
    # TODO: Replace the following line with your code which will instantiate
    #       a TCP socket with IPv4 Addressing, call the socket you make 'sock'
    # TODO: You may find that if you repeatedly run the server script it fails,
    #       claiming that the port is already used.  You can set an option on
    #       your socket that will fix this problem. We DID NOT talk about this
    #       in class. Find the correct option by reading the very end of the
    #       socket library documentation:
    #       http://docs.python.org/3/library/socket.html#example
    # log that we are building a server

    # TODO: bind your new sock 'sock' to the address above and begin to listen
    #       for incoming connections
    try:
        # the outer loop controls the creation of new connection sockets. The
        # server will handle each incoming connection one at a time.
        while True:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print("making a server on {0}:{1}".format(*address), file=log_buffer)
            sock.bind(address)
            sock.listen(1)
            print('waiting for a connection', file=log_buffer)
            conn, addr = sock.accept()
            # TODO: make a new socket when a client connects, call it 'conn',
            #       at the same time you should be able to get the address of
            #       the client so we can report it below.  Replace the
            #       following line with your code. It is only here to prevent
            #       syntax errors
            try:
                print('connection - {0}:{1}'.format(*addr), file=log_buffer)

                # the inner loop will receive messages sent by the client in
                # buffers.  When a complete message has been received, the
                # loop will exit
                while True:
                    # TODO: receive 16 bytes of data from the client. Store
                    #       the data you receive as 'data'.  Replace the
                    #       following line with your code.  It's only here as
                    #       a placeholder to prevent an error in string
                    #       formatting
                    data = conn.recv(16)
                    print('received "{0}"'.format(data.decode('utf8')))
                    conn.sendall(data)
                    # TODO: Send the data you received back to the client, log
                    # the fact using the print statement here.  It will help in
                    # debugging problems.
                    print('sent "{0}"'.format(data.decode('utf8')))
                    if len(data) < 16:
                        break
                    # TODO: Check here to see whether you have received the end
                    # of the message. If you have, then break from the `while True`
                    # loop.
                    # 
                    # Figuring out whether or not you have received the end of the
                    # message is a trick we learned in the lesson: if you don't
                    # remember then ask your classmates or instructor for a clue.
                    # :)
            except Exception as e:
                traceback.print_exc()
                sys.exit(1)
            finally:
                # TODO: When the inner loop exits, this 'finally' clause will
                #       be hit. Use that opportunity to close the socket you
                #       created above when a client connected.
                sock.close()
                print(
                    'echo complete, client connection closed', file=log_buffer
                )

    except KeyboardInterrupt:
        # TODO: Use the python KeyboardInterrupt exception as a signal to
        #       close the server socket and exit from the server function.
        #       Replace the call to `pass` below, which is only there to
        #       prevent syntax problems
        raise
        sock.close()
        print('quitting echo server', file=log_buffer)

def serverv2(log_buffer=sys.stderr):
    address = ('127.0.0.1', 10003)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("making a server on {0}:{1}".format(*address), file=log_buffer)
    sock.bind(address)
    sock.listen(5)
    print('waiting for a connection', file=log_buffer)
    inputs = [sock]
    outputs = []
    message_queues = {}
    received_message = ''
    while inputs:
        readable, writable, exceptional = select.select(
            inputs, outputs, inputs)
        for s in readable:
            if s is sock:
                connection, client_address = s.accept()
                connection.setblocking(0)
                inputs.append(connection)
                message_queues[connection] = Queue.Queue()
            else:
                data = s.recv(1024)
                print('received "{0}"'.format(data.decode('utf8')))
                connection.sendall(data)
                print('sent "{0}"'.format(data.decode('utf8')))
                if data:
                    message_queues[s].put(data)
                    if s not in outputs:
                        outputs.append(s)
                else:
                    if s in outputs:
                        outputs.remove(s)
                    inputs.remove(s)
                    s.close()
                    del message_queues[s]

        for s in writable:
            try:
                next_msg = message_queues[s].get_nowait()
            except Queue.Empty:
                outputs.remove(s)
            else:
                s.send(next_msg)

        for s in exceptional:
            inputs.remove(s)
            if s in outputs:
                outputs.remove(s)
            s.close()
            del message_queues[s]

if __name__ == '__main__':
    serverv2()
    sys.exit(0)
