#!/usr/bin/env python

# Tool to convert hex log dumps generated by onboard_logger.c on vehicle into text format matching the rest of paparazzi

import socket
import struct
import os
import logging
import sys
import threading
import string

sys.path.append(os.getenv("PAPARAZZI_HOME") + "/sw/lib/python")

import messages_xml_map

class OnboardLogTransformTool():
    def __init__(self):
      messages_xml_map.ParseMessages()
      self.data_types = { 'float' : ['f', 4],
			  'uint8' : ['B', 1],
			  'uint16' : ['H', 2],
			  'uint32' : ['L', 4],
			  'int8' : ['b', 1],
			  'int16' : ['h', 2],
			  'int32' : ['l', 4]
			 }

    def Unpack(self, data_fields, type, start, length):
	  return struct.unpack(type, "".join(data_fields[start:start + length]))[0]

    def ProcessLine(self, line):
      fields = line.strip().split(' ')
      [timestamp, ac_id, msg_id] = fields[0:3]
      data_fields = map(lambda x: chr(int(x, 16)), fields[4:])
      ac_id = int(ac_id)
      timestamp = float(timestamp)
      msg_id = int(msg_id)

      msg_name = messages_xml_map.message_dictionary_id_name[msg_id]
      msg_fields = messages_xml_map.message_dictionary_types[msg_id]

      result = "%f %i %s " % (timestamp, ac_id, msg_name)

      field_offset = 0
      for field in msg_fields:
	if field[-2:] == "[]":	
	  baseType = field[:-2]
	  array_length = int(self.Unpack(data_fields, 'B', field_offset, 1))
	  field_offset = field_offset + 1
	  for count in range(0, array_length):
	    array_value = str(self.Unpack(data_fields, self.data_types[baseType][0], field_offset, self.data_types[baseType][1]))
	    field_offset = field_offset + self.data_types[baseType][1]
	    if (count == array_length - 1):
	      result += array_value + " "
	    else:
	      result += array_value + ","
	else:
	  result += str(self.Unpack(data_fields, self.data_types[field][0], field_offset, self.data_types[field][1])) + " "
	  field_offset = field_offset + self.data_types[field][1]

	if (field_offset > len(data_fields)):
	  print "finished without parsing %s" % field
	  break

      return result[:-1]

    def Run(self, logfile):
      # open log file
      INPUT = open(logfile, "r")
      for line in INPUT:
	try:
	  print self.ProcessLine(line)
	except:
	  pass
      INPUT.close()

def main():
  log_transform = OnboardLogTransformTool()
  log_transform.Run(sys.argv[1])

if __name__ == '__main__':
  main()
