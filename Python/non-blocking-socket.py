from select import select


def nonblocking_socket_handler(readers=None, writers=None):
    readers = readers = []
    writers = writers or []
    while any([readers, writers]):
        all_read, all_write, all_err = {}, {}, {}
        read_ready, write_ready, err = select(readers, writers, readers, 60)
        for reader in read_ready:
            all_read[reader] = _read(reader)
            readers.remove(reader)
        for writer in write_ready:
            all_write[writer] = writer.write("hostname")
            writers.remove(writer)
        yield all_read, all_write, all_err

def _read(sock):
    """read the contents of a channel"""
    size, data = sock.read()
    results = ""
    while size > 0:
        try:
            results += data.decode("utf-8")
        except UnicodeDecodeError as err:
            print(f"Skipping data chunk due to {err}\nReceived: {data}")
        size, data = sock.read()
    return (results, sock.get_exit_status(), sock.read_stderr())
