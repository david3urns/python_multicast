#Python multicast script
#created by David Burns - david3urns@gmail.com
#this script is written for python 3+

#This script, when launched, will allow the user to select if they will be xmitting or receiving multicast traffic
#once listen/rec has been selected, the user will be prompted for a multicast IP and port numbers


import sys          #to allow graceful exit
import time         #to allow sleep between xmits
import socket       #to allow for IP connections
import struct       #to allow for TTL
import re           #to allow regular expression IP validation

#defining the main function
def main():
    #ask user if they will be setting up as transmit or receive, or exiting
    choice = input("Will you be transmitting or receiving? Enter 1 to transmit, 2 to receive, or 0 to exit: ")

    #user selected transmit, option 1:
    if choice == '1':
        print("Setting up as multicast transmitter.")
        ip_addr = input("Please enter the multicast IP address you would like to use: ")
        #validate the IP
        while not validate_ip(ip_addr):
            ip_addr = input("Invalid IP address, please enter a valid IP address: ")
        #ask user for port number
        port_num = int(input("Please enter the port number you would like to use for the multicast traffic: "))
        #validate port number
        while not validate_port(port_num):
            port_num = int(input("Invalid port number. Please enter a number between 1 and 65535: "))
        #ask the user for the packet TTL
        ttl_stat = int(input("Enter the TTL of the multicast packet (higher number = more hops): "))
        #ask the user how often they would like to transmit the multicast
        xmit_time = int(input("How often would you like to transmit to multicast (in seconds)?: "))
        print("Transmitting on " + str(ip_addr) + " : " + str(port_num) + " Press CTRL + C to cancel.")
        #run the xmit function with user provided information
        xmit(ip_addr, port_num, xmit_time, ttl_stat)
        
    #user selected receive, option 2
    elif choice == '2':
        print("Setting up multicast listener.")
        #asks user for multicast IP address
        ip_addr = input("Please enter the multicast IP address you would like to receive on: ")
        #asks user for multicast port number
        port_num = int(input("Please enter the port number you would like to use to receive multicast traffic: "))
        #runs the receive function
        rec(ip_addr, port_num)

    #user selected exit, option 0
    elif choice == '0':
        exit()

    #user entered something other than 1, 2, or 0
    else:
        print("Invalid entry, please select 1, 2, or 0.")


#define the validate IP function
def validate_ip(ip):
    #regular expression to match for valid IPv4 address
    ip_pattern = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
    
    #check to see if the entered IP meets the regex
    if re.match(ip_pattern, ip):
        return True
    else:
        return False

#define the validate port number function
def validate_port(port):
    try:
        port_num = int(port)
        if 0 <= port_num <= 65535:
            return True
        else:
            return False
    except ValueError:
        return False

       
def xmit(MULTICAST_GROUP, PORT, XMIT, TTL):
    #create UDP Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    #set the TTL to control scope of multicast packets
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', TTL))

    try:
        while True:
            #get current DTG
            timestamp = time.ctime()

            #send the time as multicast traffic:
            sock.sendto(timestamp.encode(), (MULTICAST_GROUP, PORT))

            #wait and retransmit:
            time.sleep(XMIT)

	        #print status of transmit:
            print(">>>>>Transmitting multicast message " + '\033[1m' + "[" + timestamp + "]"\
                   + '\033[0m' + " to " + str(MULTICAST_GROUP) + ":" + str(PORT) + ">>>>>")

    except KeyboardInterrupt:
        print("Transmit interrupted by user input.")
        pass

    finally:
        #close the socket:
        sock.close()


def rec(MULTICAST_GROUP, PORT):
    #create the UDP socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    #setup the listener:
    sock.bind(('', PORT))
    group = socket.inet_aton(MULTICAST_GROUP)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    #print status and abort instruction
    print("Listening for multicast traffic. Press CTRL + C to cancel")

    try:
        while True:
            #receive data on socket
            data, address = sock.recvfrom(1024)
            rec_info = ("<<<<<Received multicast message from " + str(MULTICAST_GROUP) + ":" + str(PORT) + ", "\
                 + '\033[1m' +  "[" + str(data) + "]" + '\033[0m' + "<<<<<")
            strip_info = rec_info.replace("b", "")
            strip_info = strip_info.replace("'", "")
            print(strip_info)
    except KeyboardInterrupt:
        print("Listener stopped by user input.")
        pass

    finally:
        #close the socket
        sock.close()

main()
