from ctypes.util import find_library
import ctypes
from numpy.ctypeslib import ndpointer
import platform
import sys
import threading
from typing import cast

from nidaqmx.errors import DaqNotFoundError, DaqNotSupportedError, DaqFunctionNotSupportedError


_DAQ_NOT_FOUND_MESSAGE = "Could not find an installation of NI-DAQmx. Please ensure that NI-DAQmx " \
                         "is installed on this machine or contact National Instruments for support."

_DAQ_NOT_SUPPORTED_MESSAGE = "NI-DAQmx Python is not supported on this platform: {0}. Please " \
                             "direct any questions or feedback to National Instruments."

_FUNCTION_NOT_SUPPORTED_MESSAGE = "The NI-DAQmx function \"{0}\" is not supported in this version " \
                                  "of NI-DAQmx. Visit ni.com/downloads to upgrade."


class c_bool32(ctypes.c_uint):
    """
    Specifies a custom ctypes data type to represent 32-bit booleans.
    """

    # typeshed specifies that _SimpleCData[_T].value is an instance variable with type _T, so
    # accessing it with the descriptor protocol via its class results in "error: Access to generic
    # instance variables via class is ambiguous".

    def _getter(self):
        return bool(ctypes.c_uint.value.__get__(self))  # type: ignore

    def _setter(self, val):
        ctypes.c_uint.value.__set__(self, int(val))  # type: ignore

    value: bool = cast(bool, property(_getter, _setter))

    del _getter, _setter


class CtypesByteString:
    """
    Custom argtype that automatically converts unicode strings to ASCII
    strings in Python 3.
    """
    @classmethod
    def from_param(cls, param):
        if isinstance(param, str):
            param = param.encode('ascii')
        return ctypes.c_char_p(param)


ctypes_byte_str = CtypesByteString


def wrapped_ndpointer(*args, **kwargs):
    """
    Specifies an ndpointer type that wraps numpy.ctypeslib.ndpointer and
    allows a value of None to be passed to an argument of that type.

    Taken from http://stackoverflow.com/questions/32120178
    """
    base = ndpointer(*args, **kwargs)

    def from_param(cls, obj):
        if obj is None:
            return obj
        return base.from_param(obj)

    return type(base.__name__, (base,),
                {'from_param': classmethod(from_param)})


class DaqFunctionImporter:
    """
    Wraps the function getter function of a ctypes library.

    Allows the NI-DAQmx Python API to fail elegantly if a function is not
    supported in the current version of the API.
    """

    def __init__(self, library):
        self._library = library
        self._lib_lock = threading.Lock()

    def __getattr__(self, function):
        try:
            cfunc = getattr(self._library, function)
            if not hasattr(cfunc, 'arglock'):
                with self._lib_lock:
                    if not hasattr(cfunc, 'arglock'):
                        cfunc.arglock = threading.Lock()
            return cfunc
        except AttributeError:
            raise DaqFunctionNotSupportedError(_FUNCTION_NOT_SUPPORTED_MESSAGE.format(function))


class DaqLibImporter:
    """
    Encapsulates NI-DAQmx library importing and handle type parsing logic.
    """

    def __init__(self):
        self._windll = None
        self._cdll = None
        self._cal_handle = None
        self._task_handle = None

    @property
    def windll(self):
        if self._windll is None:
            self._import_lib()
        return self._windll

    @property
    def cdll(self):
        if self._cdll is None:
            self._import_lib()
        return self._cdll

    @property
    def task_handle(self):
        if self._task_handle is None:
            self._parse_typedefs()
        return self._task_handle

    @property
    def cal_handle(self):
        if self._cal_handle is None:
            self._parse_typedefs()
        return self._cal_handle

    def _import_lib(self):
        """
        Determines the location of and loads the NI-DAQmx CAI DLL.
        """
        self._windll = None
        self._cdll = None

        windll = None
        cdll = None

        if sys.platform.startswith('win') or sys.platform.startswith('cli'):
            try:
                if 'iron' in platform.python_implementation().lower():
                    windll = ctypes.windll.nicaiu
                    cdll = ctypes.cdll.nicaiu
                else:
                    windll = ctypes.windll.LoadLibrary('nicaiu')
                    cdll = ctypes.cdll.LoadLibrary('nicaiu')
            except (OSError, WindowsError) as e:
                raise DaqNotFoundError(_DAQ_NOT_FOUND_MESSAGE) from e
        elif sys.platform.startswith('linux'):
            # On linux you can use the command find_library('nidaqmx')
            if find_library('nidaqmx') is not None:
                cdll = ctypes.cdll.LoadLibrary(find_library('nidaqmx'))
                windll = cdll
            else:
                raise DaqNotFoundError(_DAQ_NOT_FOUND_MESSAGE)
        else:
            raise DaqNotSupportedError(_DAQ_NOT_SUPPORTED_MESSAGE.format(sys.platform))

        self._windll = DaqFunctionImporter(windll)
        self._cdll = DaqFunctionImporter(cdll)

    @staticmethod
    def _get_task_handle_type(driver_version):
        """
        Determines the ctypes data types of the Task handle based on the version of
        the NI-DAQmx driver installed. DAQmx 8.9 added 64-bit support, and the
        handle was changed to an opaque pointer.
        """
        return ctypes.c_void_p if driver_version >= (8,9,0) else ctypes.c_uint

    def _parse_typedefs(self):
        """
        Determines the ctypes data types of the Task and Cal handles
        based on the version of the NI-DAQmx driver installed.
        """
        from nidaqmx.system.system import System
        system = System.local()

        self._task_handle = DaqLibImporter._get_task_handle_type(system.driver_version)
        self._cal_handle = ctypes.c_uint


lib_importer = DaqLibImporter()
