from . import *
from udsoncan.Response import Response
from udsoncan.exceptions import *
import struct

class RoutineControl(BaseService):
    # _sid = 0x30
    _use_subfunction = False

    class ControlType(BaseSubfunction):
        """
        RoutineControl defined subfunctions
        """		
        __pretty_name__ = 'control type'
    
        startRoutine = 1
        stopRoutine = 2
        requestRoutineResults = 3

    supported_negative_response = [	 Response.Code.IncorrectMessageLegthOrInvalidFormat,
                                                    Response.Code.ConditionsNotCorrect,
                                                    Response.Code.RequestSequenceError,
                                                    Response.Code.RequestOutOfRange,
                                                    Response.Code.SecurityAccessDenied,
                                                    Response.Code.GeneralProgrammingFailure
                                                    ]

    @classmethod
    def make_request(cls, routine_id, control_type, data=None):
        """
        Generates a request for RoutineControl

        :param routine_id: The routine ID. Value should be between 0 and 0xFFFF
        :type routine_id: int

        :param data: Optional additional data to provide to the server
        :type data: bytes

        :raises ValueError: If parameters are out of range, missing or wrong type
        """		
        from udsoncan import Request

        ServiceHelper.validate_int(routine_id, min=0, max=0xFF, name='Routine ID')
        ServiceHelper.validate_int(control_type, min=0, max=0x7F, name='Routine control type')

        if data is not None:
            if not isinstance(data, bytes):
                raise ValueError('data must be a valid bytes object')

        RoutineControl._sid = 0x30 + control_type
        request = Request(service=cls) # control_type)
        request.data = struct.pack('>B', routine_id)
        if data is not None:
            request.data += data

        return request

    @classmethod
    def interpret_response(cls, response):
        """
        Populates the response ``service_data`` property with an instance of :class:`RoutineControl.ResponseData<udsoncan.services.RoutineControl.ResponseData>`

        :param response: The received response to interpret
        :type response: :ref:`Response<Response>`

        :raises InvalidResponseException: If length of ``response.data`` is too short
        """

        if len(response.data) < 1: ### GGGG era 3: 	
            raise InvalidResponseException(response, "Response data must be at least 3 bytes")

        response.service_data = cls.ResponseData()
        # response.service_data.routine_id_echo = struct.unpack(">B", response.data[0])[0]
        response.service_data.routine_id_echo = response.data[0]
        response.service_data.control_type_echo = cls._sid - 0x30
        # response.service_data.routine_status_record = response.data[1:] if len(response.data) >1 else b''

    class ResponseData(BaseResponseData):
        """
        .. data:: routine_id_echo

                Requests routine ID echoed back by the server.

        .. data:: routine_status_record

                Additional data associated with the response.
        """		
        def __init__(self):
            super().__init__(RoutineControl)

            self.routine_id_echo = None
            self.routine_status_record = None

# class RoutineControl_startRoutine(RoutineControl):
#     _sid = 0x31
# 
# class RoutineControl_stopRoutine(RoutineControl):
#     _sid = 0x32
# 
# class RoutineControl_requestRoutineResults(RoutineControl):
#     _sid = 0x33

