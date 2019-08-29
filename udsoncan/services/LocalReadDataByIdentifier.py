from . import *
from udsoncan.Response import Response
from udsoncan.exceptions import *
import struct

class LocalReadDataByIdentifier(ReadDataByIdentifier, BaseService):
	_sid = 0x21
	@classmethod
	def make_request(cls, didlist, didconfig):
		from udsoncan import Request
		didlist = cls.validate_didlist_input(didlist)
		req = Request(cls)
		ServiceHelper.check_did_config(didlist, didconfig)
		req.data = struct.pack('>'+'B'*len(didlist), *didlist) #Encode list of DID
		return req
	@classmethod
	def interpret_response(cls, response, didlist, didconfig, tolerate_zero_padding=True):
		from udsoncan import DidCodec

		didlist = cls.validate_didlist_input(didlist)
		didconfig = ServiceHelper.check_did_config(didlist, didconfig)
		
		response.service_data = cls.ResponseData()
		response.service_data.values = {}

		# Parsing algorithm to extract DID value
		offset = 0
		while True:
			if len(response.data) <= offset:
				break	# Done

			if len(response.data) <= offset +1:
				if tolerate_zero_padding and response.data[-1] == 0:	# One extra byte, but it's a 0 and we accept that. So we're done
					break
				raise InvalidResponseException(response, "Response given by server is incomplete.")

			did = struct.unpack('>B', response.data[offset:offset+1])[0]	# Get the DID number GGGG era +2 e >H
			#print(">>>>>>>>>>>>> DID =%s" % did)
			if did == 0 and did not in didconfig and tolerate_zero_padding: # We read two zeros and that is not a DID bu we accept that. So we're done.
				if response.data[offset:] == b'\x00' * (len(response.data) - offset):
					break

			if did not in didconfig:	# Already checked in check_did_config. Paranoid check
				raise ConfigError(key=did, msg='Actual data identifier configuration contains no definition for data identifier 0x%04x' % did)
			
			codec = DidCodec.from_config(didconfig[did])
			#print("codec=%s" % codec)
			offset+=1 # GGG

			if len(response.data) < offset+len(codec):
				raise InvalidResponseException(response, "Value for data identifier 0x%04x was incomplete according to definition in configuration" % did)

			subpayload = response.data[offset:offset+len(codec)]
			#print("subplayload=%s" % subpayload)
			offset += len(codec)	# Codec must define a __len__ function that matches the encoded payload length.
			val = codec.decode(subpayload)
			#print("val=%s" % val)
			response.service_data.values[did] = val

		return response

# udsoncan.services.LocalReadDataByIdentifier = LocalReadDataByIdentifier
