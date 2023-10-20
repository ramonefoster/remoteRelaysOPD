import socket
import select
import time

class AsciiIo:
    """Example class for communication with Brainboxes ED-range products
    Tested with Python 2.7.9 and 3.4.3 on Windows, and 2.7.6 and 3.4.0 on Linux
    """
    
    def __init__(self, ipaddr, port=9500, timeout=5.0):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((ipaddr, port))
            self.status = True
        except (ConnectionRefusedError, OSError) as e:
            print(f"Error connecting to the server: {e}")
            self.status = False
            # Handle the error here, e.g., log it or raise an exception as needed.
            self.sock = None
        self.timeout = timeout
        self.recv_chunk_size = 32
         

    def command_noresponse(self, txmessage):
        try:
            self._send(txmessage)
            self.status = True
        except Exception as e:
            print(f"Error sending data: {e}")
            self.status = False
            # Handle the error here, you can raise an exception or log it as needed.

    def command_response(self, txmessage):
        try:
            self._send(txmessage)
            self.status = True
            return self._receive()
        except Exception as e:
            print(f"Error sending or receiving data: {e}")
            self.status = False
            # Handle the error here, you can raise an exception or log it as needed.
            return None  # You can also return None or some other value to indicate the error.

    def _send(self, txmessage):
        txmessage = txmessage + b"\r"
        totalsent = 0
        while totalsent < len(txmessage):
            try:
                bytes_sent = self.sock.send(txmessage[totalsent:])
                if bytes_sent == 0:
                    raise RuntimeError("socket connection broken")
                totalsent += bytes_sent
                self.status = True
            except Exception as e:
                print(f"Error sending data: {e}")
                self.status = False
                # Handle the error here, you can raise an exception or log it as needed.

    def _receive(self):
        tstart = time.time()
        data = b''
        endpos = -1
        while endpos < 0:
            tleft = max(0.0, tstart + self.timeout - time.time())
            ready_to_read, _, in_error = select.select([self.sock], [], [self.sock], tleft)
            if len(in_error) > 0:
                raise RuntimeError("error on socket connection")
            if len(ready_to_read) > 0:
                try:
                    chunk = self.sock.recv(self.recv_chunk_size)
                    if chunk == b'':
                        raise RuntimeError("socket connection broken")
                    data += chunk
                    endpos = data.find(b'\r')
                    self.status = True
                except Exception as e:
                    print(f"Error receiving data: {e}")
                    self.status = False
                    # Handle the error here, you can raise an exception or log it as needed.
            elif tleft == 0.0:
                # Handle timeout as needed.
                return None
        return data[:endpos]
            
    def _destructor(self):
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except Exception as e:
            # Ignore any failures to shutdown and close the socket - it's probably already closed.
            pass

    def __del__(self):
        self._destructor()

    def __enter__(self):
        return self
        
    def __exit__(self, type, value, traceback):
        self._destructor()
