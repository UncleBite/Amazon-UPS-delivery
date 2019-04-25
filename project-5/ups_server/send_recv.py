from google.protobuf.internal.encoder import _EncodeVarint
from google.protobuf.internal.decoder import _DecodeVarint32
import world_ups_pb2
import ups_amazon_pb2
import psycopg2
from time import sleep
from protobuf_json import json2pb

db_host = "localhost"
db_port = "5432"
seq = 0

def send_unack_msg_to_world(worldfd):
    db_conn = psycopg2.connect("dbname='postgres' user='postgres' password = 'passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'")
    db_cur = db_conn.cursor()
    while True:
        """
        get all message that haven't receive ack
        """
        db_cur.execute("""select message from  world_ack""")
        """send them all again"""
        msgs_json = db_cur.fetchall()
        """define json format, restore it back to Message"""
        for msg_json in msgs_json:
            """restore it back to Message and send again"""
            msg = world_ups_pb2.UCommands()
            msg = json2pb(msg, msg_json, useFieldNumber=False)
            _EncodeVarint(worldfd.send, len(msg.SerializeToString()), None)
            worldfd.sendall(msg.SerializeToString())
        sleep(60)

def send_unack_msg_to_amazon(amazon_fd):
    db_conn = psycopg2.connect("dbname='postgres' user='postgres' password = 'passw0rd'"
                               "host='" + db_host + "' port='" + db_port + "'")
    db_cur = db_conn.cursor()
    while True:
        """
        get all message that haven't receive ack
        """
        db_cur.execute("""select message from  amazon_ack""")
        """send them all again"""
        msgs_json = db_cur.fetchall()
        for msg_json in msgs_json:
            """restore it back to Message and send again"""
            msg = ups_amazon_pb2.UCommunicate()
            msg = json2pb(msg, msg_json, useFieldNumber=False)
            _EncodeVarint(amazon_fd.send, len(msg.SerializeToString()), None)
            amazon_fd.sendall(msg.SerializeToString())
        sleep(60)


def disconnect(world_fd):
    UCommands = ups_amazon_pb2.UCommands()
    UCommands.disconnect = True
    acks = UCommands.acks.add()
    acks.ack = get_seqnum()
    while True:
        send_to_world(UCommands,world_fd)
        if acks.ack in world_ack_list:
            break


def get_seqnum():
    global seq
    seq = seq+1
    return seq

def send_ack_to_amazon(ack, amazon_fd):
    #print("sending ack to AMAZON")
    UCommu = ups_amazon_pb2.UCommunicate()
    UCommu.acks.append(ack)
    send_to_amazon(UCommu,amazon_fd)

def send_ack_to_world(ack, world_fd):
    #print("sending ack to WORLD")
    UCommands = world_ups_pb2.UCommands()
    UCommands.acks.append(ack)
    send_to_world(UCommands,world_fd)

def send_to_world(msg, worldfd):
    #print('msg you send to WORLD is:')
    print(msg)
    _EncodeVarint(worldfd.send, len(msg.SerializeToString()), None)
    worldfd.sendall(msg.SerializeToString())

def send_to_amazon(msg, amazon_fd):
    #print('msg you send to AMAZON is')
    print(msg)
    _EncodeVarint(amazon_fd.send, len(msg.SerializeToString()), None)
    amazon_fd.sendall(msg.SerializeToString())

def recv_from_world(Message, world_fd):
    var_int_buff = []
    while True:
        try:
            buf = world_fd.recv(1)
            var_int_buff += buf
            msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
            if new_pos != 0:
                break
        except:
            continue
    whole_message = world_fd.recv(msg_len)
    Message.ParseFromString(whole_message)
    #print("message received from WORLD is:")
    #print(Message)
    return (Message)

def recv_from_amazon(Message, amazon_fd):
    var_int_buff = []
    while True:
        try:
            buf = amazon_fd.recv(1)
            var_int_buff += buf
            msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
            if new_pos != 0:
                break
        except:
            continue
    whole_message = amazon_fd.recv(msg_len)
    Message.ParseFromString(whole_message)
    #print("message received from AMAZON is:")
    #print(Message)
    return (Message)
