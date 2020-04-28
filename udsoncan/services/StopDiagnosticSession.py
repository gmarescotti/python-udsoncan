"""
Adaptation for Keyword 2000 compatibility
"""

from . import *
from udsoncan.Response import Response
from udsoncan.exceptions import *

class StopDiagnosticSession(BaseService):
    _sid = 0x20
    _use_subfunction = False

    supported_negative_response = [	Response.Code.SubFunctionNotSupported, 
                                        Response.Code.IncorrectMessageLegthOrInvalidFormat
                                        ]	

    @classmethod
    def make_request(cls):
        """
        Generates a request for StopDiagnosticSession
        """		
        from udsoncan import Request
        return Request(service=cls)

    @classmethod
    def interpret_response(cls, response):
        """
        Populates the response ``service_data`` property with an instance of :class:`StopDiagnosticSession.ResponseData<udsoncan.services.StopDiagnosticSession.ResponseData>`

        :param response: The received response to interpret
        :type response: :ref:`Response<Response>`

        :raises InvalidResponseException: If length of ``response.data`` is too short
        """		
        if  len(response.data) < 1:
            raise InvalidResponseException(response, "Response data must be at least 1 bytes")

        response.service_data = cls.ResponseData()
        response.service_data.subfunction_echo = response.data[0]

    class ResponseData(BaseResponseData):
        """
        .. data:: subfunction_echo

                Requests subfunction echoed back by the server. This value should always be 0
        """		
        def __init__(self):
            super().__init__(StopDiagnosticSession)
            self.subfunction_echo = None