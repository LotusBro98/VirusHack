import bluetooth

uuid = "00001101-0000-1000-8000-00805F9B34FB"

server_socket = bluetooth.BluetoothSocket( bluetooth.RFCOMM )

server_socket.bind(("", bluetooth.PORT_ANY))
server_socket.listen(1)
bluetooth.advertise_service(server_socket, "sampleserver",
        service_id=uuid,
        service_classes=[uuid,
                         bluetooth.SERIAL_PORT_CLASS],
        profiles=[bluetooth.SERIAL_PORT_PROFILE])

while True:
    client_socket, address = server_socket.accept()
    data = client_socket.recv(1024)
    print("received [%s]" % data)
    client_socket.close()

server_socket.close()