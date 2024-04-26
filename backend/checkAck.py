from ack import ack_list
from mysocket import *
from protocal import world_amazon_pb2 as world
from protocal import web_backend_pb2 as web
from protocal import amazon_ups_pb2 as ups
import time


# send request until receive ack
def checkAndSendReq(fd, req_msg, seqNum ):
    print("checkAndSendReq seqNum: ", seqNum)
    while True:
        # check ack in seq_list: resend
        print("pending set: ",ack_list.pending_acks)
        if seqNum in ack_list.pending_acks:
            print("still in list" )
            sendRequest(fd, req_msg)
            time.sleep(2)  # waits for 2 seconds
        # otherwise break
        else:
            print("break")
            break
        
def sendAck_world(fd, seqNum):
    print("enter sendAck_world")
    req_msg = world.ACommands()
    req_msg.acks.append(seqNum)
    sendRequest(fd, req_msg)
    print("after enter sendAck_world")
    
def sendAck_web(fd, seqNum):
    print("enter sendAck_web")
    req_msg = web.BResponse()
    req_msg.acks.append(seqNum)
    sendRequest(fd, req_msg)
    print("after enter sendAck_web")
    
def sendAck_ups(fd, seqNum):
    print("enter sendAck_ups")
    req_msg = ups.ACommand()
    req_msg.acks.append(seqNum)
    sendRequest(fd, req_msg)
    print("after enter sendAck_ups")