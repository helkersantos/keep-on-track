import os
import sys
import struct
import bluetooth._bluetooth as bluez
import socket
import time
import json
import asyncio
import logging
import random
from datetime import datetime
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message


filtrobeacon1 = 'ac'			#Filtro de MAC beacon byte 1
filtrobeacon2 = '23'			#Filtro de MAC beacon byte 2
filtrooff = 'ON'				#Filtro ON/OFF
#-------------------------------------------------------------
coletor_local = socket.gethostname()		# Nome do Dispositivo Raspberry conforme estiver na rede
logger = logging.getLogger("azure")

CONNECTION_STRING = "HostName=UpmHubIot.azure-devices.net;DeviceId=teste;SharedAccessKey=6uVa+nZHKkYrn0wcySFfilrgJzXFs/gCaTCWtDwE8fo="

#------------------------------------------------------------



LE_META_EVENT = 0x3e
OGF_LE_CTL=0x08
OCF_LE_SET_SCAN_ENABLE=0x000C

# these are actually subevents of LE_META_EVENT
EVT_LE_CONN_COMPLETE=0x01
EVT_LE_ADVERTISING_REPORT=0x02

def getBLESocket(devID):
	return bluez.hci_open_dev(devID)


def returnstringpacket(pkt):
    myString = "";
    for i in range(len(pkt)):
        myString += "%02x" %struct.unpack("B",pkt[i:i+1])[0]
    return myString


def get_packed_bdaddr(bdaddr_string):
    packable_addr = []
    addr = bdaddr_string.split(':')
    addr.reverse()
    for b in addr:
        packable_addr.append(int(b, 16))
    return struct.pack("<BBBBBB", *packable_addr)

def packed_bdaddr_to_string(bdaddr_packed):
    return ':'.join('%02x'%i for i in struct.unpack("<BBBBBB", bdaddr_packed[::-1]))

def hci_enable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x01)

def hci_disable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x00)

def hci_toggle_le_scan(sock, enable):
    cmd_pkt = struct.pack("<BB", enable, 0x00)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)

def hci_le_set_scan_parameters(sock):
    old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)
    return old_filter

def parse_events(sock, loop_count=100):
    old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)
    flt = bluez.hci_filter_new()
    bluez.hci_filter_all_events(flt)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, flt )
    myFullList = []
    for i in range(0, loop_count):
        pkt = sock.recv(255)
        ptype, event, plen = struct.unpack("BBB", pkt[:3])
        if event == bluez.EVT_INQUIRY_RESULT_WITH_RSSI:
            i = 0
        elif event == bluez.EVT_NUM_COMP_PKTS:
            i = 0
        elif event == bluez.EVT_DISCONN_COMPLETE:
            i = 0
        elif event == LE_META_EVENT:
            subevent, = struct.unpack("B", pkt[3:4])
            pkt = pkt[4:]
            if subevent == EVT_LE_CONN_COMPLETE:
                le_handle_connection_complete(pkt)
            elif subevent == EVT_LE_ADVERTISING_REPORT:
                num_reports = struct.unpack("B", pkt[0:1])[0]
                report_pkt_offset = 0
                for i in range(0, num_reports):
                    # build the return string
                    Adstring = packed_bdaddr_to_string(pkt[report_pkt_offset + 3:report_pkt_offset + 9])
                    Adstring += ',' + returnstringpacket(pkt)
                    Adstring += ',' + returnstringpacket(pkt[report_pkt_offset -6: report_pkt_offset - 4])
                    Adstring += ',' + returnstringpacket(pkt[report_pkt_offset -4: report_pkt_offset - 2])
                    try:
                        Adstring += ',' + returnstringpacket(pkt[report_pkt_offset -2:report_pkt_offset -1])
                    except: 1
                    #Prevent duplicates in results
                    if Adstring not in myFullList: myFullList.append(Adstring)
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, old_filter )
    return myFullList

if __name__ == '__main__':
	dev_id = 0
	coletor_local = socket.gethostname()
	try:
		sock = bluez.hci_open_dev(dev_id)
		print("In??cio da execu????o")
	except:
		print("Erro de acesso ao dispositivo bluetooth...")
		sys.exit(1)

	teste = hci_le_set_scan_parameters(sock)
	hci_enable_le_scan(sock)

	while True:
		g = time.time()
		returnedList = parse_events(sock, 20)
				
		try:
			# Create Hub Iot client
			client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
			
			try:
				
				start_time = time.time()				
				for beacon in returnedList:
	
					a = beacon.split(',')[0] #Convers??o do MAC Addr para o valor convencional de visualizacao
					b = beacon.split(',')[1] #Todo o protocolo enviado
					rssi = int(b[-2::],16) - 0xff
					rssi1m = int(b[-4:-2],16) - 0xff
					if (a.split(':')[0] == 'ac' and a.split(':')[1] == '23') or filtrooff == 'OFF':
						#print('\n')
						if b[26:34]== '0303aafe':				
							if b[38:44] == 'aafe20':
								tipo = 'ble_eddystone_tlm'
								eventjson= json.dumps({'MAC': a,'Protocolo': b,'Tipo': tipo,'Bateria': int(b[46:50],16),'Temperatura': int(b[50:52],16),'PUD Count': int(b[54:62],16),'Tempo de Reboot': int(b[62:70],16),'RSSI': rssi,'Data': g,'Coletor': coletor_local})  
								print (eventjson)
								client.send_message(eventjson)
							elif b[38:44] == 'aafe00':
								tipo = 'ble_eddystone_uid'
								eventjson= json.dumps({'MAC': a,'Protocolo': b,'Tipo': tipo,'Namespace': b[46:66],'Instance': b[66:78],'RSSI': rssi,'Data': g,'Coletor': coletor_local}) 
								print (eventjson)
								client.send_message(eventjson)
							elif b[38:44] == 'aafe10':
								tipo = 'ble_eddystone_url'
								if b[46:48] == '00':
									prefix = 'http://www.'
								elif b[46:48] == '01':
									prefix = 'https://www.'
								elif b[46:48] == '02':
									prefix = 'http://'
								elif b[46:48] == '03':
									prefix = 'https://'
								else:
									prefix = ' '
								if b[-4:-2] == '00':
									encoding = '.com/'
								elif b[-4:-2] == '01':
									encoding = '.org/'
								elif b[-4:-2] == '02':
									encoding = '.edu/'
								elif b[-4:-2] == '03':
									encoding = '.net/'
								elif b[-4:-2] == '04':
									encoding = '.info/'
								elif b[-4:-2] == '05':
									encoding = '.biz/'
								elif b[-4:-2] == '06':
									encoding = '.gov/'
								elif b[-4:-2] == '07':
									encoding = '.com'
								elif b[-4:-2] == '08':
									encoding = '.org'
								elif b[-4:-2] == '09':
									encoding = '.edu'
								elif b[-4:-2] == '0a':
									encoding = '.net'
								elif b[-4:-2] == '0b':
									encoding = '.info'
								elif b[-4:-2] == '0c':
									encoding = '.biz'
								elif b[-4:-2] == '0d':
									encoding = '.gov'				
								else:
									encoding = ' '
								link = str(prefix + bytes.fromhex(b[48:-2]).decode('utf-8') + encoding)
								eventjson= json.dumps({'MAC': a,'Protocolo': b,'Tipo': tipo,'Link': link ,'RSSI': rssi,'Data': g,'Coletor': coletor_local})
								print (eventjson)
								client.send_message(eventjson)
							else:
								tipo = 'ble_eddystone_eid'
								eventjson= json.dumps({'MAC': a,'Protocolo': b,'Tipo': tipo,'UUID': b[38:70],'RSSI': rssi,'Data': g,'Coletor': coletor_local}) 
								print (eventjson)
								client.send_message(eventjson)
						elif b[26:34]== '1aff4c00':
							tipo = 'ble_apple_ibeacon'
							eventjson= json.dumps({'MAC': a,'Protocolo': b,'Tipo': tipo,'UUID': b[38:70],'Major': b[70:74],'Minor': b[74:78],'Tx at 1m': rssi1m,'RSSI': rssi,'Data': g,'Coletor': coletor_local}) 
							print (eventjson)
							client.send_message(eventjson)

						elif b[26:34]== '0303f1ff':
							tipo = 'ble_indet_beacon'
							eventjson= json.dumps({'MAC': a,'Protocolo': b,'Tipo': tipo,'UUID': b[38:70],'Major': int(b[-14:-10],16),'Minor': int(b[-10:-6],16),'RSSI': rssi,'Data': g,'Coletor': coletor_local}) 
							client.send_message(eventjson)
						else:
							tipo = 'bluetooth'
							eventjson= json.dumps({'MAC': a,'Protocolo': b,'Tipo': tipo,'Data': g,'local': coletor_local}) 
							print (eventjson)
							client.send_message(eventjson)
			except:
				raise
			finally:
				end_time = time.time()
				client.stop()
				run_time = end_time - start_time
				logger.info("Runtime: {} seconds".format(run_time))

		except:
			print('erro de envio')
			for beacon in returnedList:		
				a = beacon.split(',')[0] #Convers??o do MAC Addr para o valor convencional de visualizacao
				b = beacon.split(',')[1] #Todo o protocolo enviado
				rssi = int(b[-2::],16) - 0xff
				rssi1m = int(b[-4:-2],16) - 0xff
				if (a.split(':')[0] == 'ac' and a.split(':')[1] == '23') or filtrooff == 'OFF':
					print('\n')
					if b[26:34]== '0303aafe':				
						if b[38:44] == 'aafe20':
							tipo = 'ble_eddystone_tlm'
							eventjson= json.dumps({'MAC': a,'Protocolo': b,'Tipo': tipo,'Bateria': int(b[46:50],16),'Temperatura': int(b[50:52],16),'PUD Count': int(b[54:62],16),'Tempo de Reboot': int(b[62:70],16),'RSSI': rssi,'Data': g,'Coletor': coletor_local})  
							fp = open('errosdeenvio.json', 'a')
							fp.write(eventjson +'\n')
							fp.close()
							print (eventjson)
						elif b[38:44] == 'aafe00':
							tipo = 'ble_eddystone_uid'
							eventjson= json.dumps({'MAC': a,'Protocolo': b,'Tipo': tipo,'Namespace': b[46:66],'Instance': b[66:78],'RSSI': rssi,'Data': g,'Coletor': coletor_local})  
							fp = open('errosdeenvio.json', 'a')
							fp.write(eventjson +'\n')
							fp.close()
							print (eventjson)
						elif b[38:44] == 'aafe10':
							tipo = 'ble_eddystone_url'
							if b[46:48] == '00':
								prefix = 'http://www.'
							elif b[46:48] == '01':
								prefix = 'https://www.'
							elif b[46:48] == '02':
								prefix = 'http://'
							elif b[46:48] == '03':
								prefix = 'https://'
							else:
								prefix = ' '
							if b[-4:-2] == '00':
								encoding = '.com/'
							elif b[-4:-2] == '01':
								encoding = '.org/'
							elif b[-4:-2] == '02':
								encoding = '.edu/'
							elif b[-4:-2] == '03':
								encoding = '.net/'
							elif b[-4:-2] == '04':
								encoding = '.info/'
							elif b[-4:-2] == '05':
								encoding = '.biz/'
							elif b[-4:-2] == '06':
								encoding = '.gov/'
							elif b[-4:-2] == '07':
								encoding = '.com'
							elif b[-4:-2] == '08':
								encoding = '.org'
							elif b[-4:-2] == '09':
								encoding = '.edu'
							elif b[-4:-2] == '0a':
								encoding = '.net'
							elif b[-4:-2] == '0b':
								encoding = '.info'
							elif b[-4:-2] == '0c':
								encoding = '.biz'
							elif b[-4:-2] == '0d':
								encoding = '.gov'				
							else:
								encoding = ' '
							link = str(prefix + bytes.fromhex(b[48:-2]).decode('utf-8') + encoding)
							eventjson= json.dumps({'MAC': a,'Protocolo': b,'Tipo': tipo,'Link': link ,'RSSI': rssi,'Data': g,'Coletor': coletor_local})
							fp = open('errosdeenvio.json', 'a')
							fp.write(eventjson +'\n')
							fp.close()							
							print (eventjson)
						else:
							tipo = 'ble_eddystone_eid'
							eventjson= json.dumps({'MAC': a,'Protocolo': b,'Tipo': tipo,'UUID': b[38:70],'RSSI': rssi,'Data': g,'Coletor': coletor_local}) 
							fp = open('errosdeenvio.json', 'a')
							fp.write(eventjson +'\n')
							fp.close()
							print (eventjson)
					elif b[26:34]== '1aff4c00':
						tipo = 'ble_apple_ibeacon'
						eventjson= json.dumps({'MAC': a,'Protocolo': b,'Tipo': tipo,'UUID': b[38:70],'Major': b[70:74],'Minor': b[74:78],'Tx at 1m': rssi1m,'RSSI': rssi,'Data': g,'Coletor': coletor_local})  
						fp = open('errosdeenvio.json', 'a')
						fp.write(eventjson +'\n')
						fp.close()
						print (eventjson)
					elif b[26:34]== '0303f1ff':
						tipo = 'ble_indet_beacon'
						eventjson= json.dumps({'MAC': a,'Protocolo': b,'Tipo': tipo,'UUID': b[38:70],'Major': int(b[-14:-10],16),'Minor': int(b[-10:-6],16),'RSSI': rssi,'Data': g,'Coletor': coletor_local})  
						fp = open('errosdeenvio.json', 'a')
						fp.write(eventjson +'\n')
						fp.close()
						print (eventjson)						
					else:
						tipo = 'bluetooth'
						eventjson= json.dumps({'MAC': a,'Protocolo': b,'Tipo': tipo,'Data': g,'local': coletor_local})  
						fp = open('errosdeenvio.json', 'a')
						fp.write(eventjson +'\n')
						fp.close()
						print (eventjson)
