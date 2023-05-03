<%
    from codegen.utilities.text_wrappers import wrap
    from codegen.utilities.function_helpers import get_functions
    from codegen.utilities.attribute_helpers import get_attributes,  get_enums_used
    from codegen.utilities.text_wrappers import wrap
    attributes = get_attributes(data, "Device")
    functions = get_functions(data,"Device")
    enums_used = get_enums_used(attributes)
%>\
# Do not edit this file; it was automatically generated.

import ctypes
import numpy
import deprecation

from nidaqmx import utils
from nidaqmx._lib import (
    lib_importer, wrapped_ndpointer, enum_bitfield_to_list, ctypes_byte_str,
    c_bool32)
from nidaqmx.errors import (
    check_for_error, is_string_buffer_too_small, is_array_buffer_too_small)
from nidaqmx.utils import unflatten_channel_string
from nidaqmx.system._collections.physical_channel_collection import (
    AIPhysicalChannelCollection, AOPhysicalChannelCollection,
    CIPhysicalChannelCollection, COPhysicalChannelCollection,
    DILinesCollection, DIPortsCollection, DOLinesCollection, DOPortsCollection)
%if enums_used:
from nidaqmx.constants import (
    ${', '.join([c for c in enums_used]) | wrap(4, 4)})
%endif

__all__ = ['Device']


class Device:
    """
    Represents a DAQmx device.
    """
    __slots__ = ['_name', '_interpreter', '__weakref__']

    def __init__(self, name, *, grpc_options=None):
        """
        Args:
            name (str): Specifies the name of the device.
            grpc_options (Optional[GrpcSessionOptions]): Specifies the gRPC session options.
        """
        self._name = name
        self._interpreter = utils._select_interpreter(grpc_options)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._name == other._name
        return False

    def __hash__(self):
        return hash(self._name)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return f'Device(name={self._name})'

    @property
    def name(self):
        """
        str: Specifies the name of this device.
        """
        return self._name

    # region Physical Channel Collections

    @property
    def ai_physical_chans(self):
        """
        List[nidaqmx.system._collections.PhysicalChannelCollection]:
            Indicates a collection that contains all the analog input
            physical channels available on the device.
        """
        return AIPhysicalChannelCollection(self._name, self._interpreter)

    @property
    def ao_physical_chans(self):
        """
        List[nidaqmx.system._collections.PhysicalChannelCollection]:
            Indicates a collection that contains all the analog output
            physical channels available on the device.
        """
        return AOPhysicalChannelCollection(self._name, self._interpreter)

    @property
    def ci_physical_chans(self):
        """
        List[nidaqmx.system._collections.PhysicalChannelCollection]:
            Indicates a collection that contains all the counter input
            physical channels available on the device.
        """
        return CIPhysicalChannelCollection(self._name, self._interpreter)

    @property
    def co_physical_chans(self):
        """
        List[nidaqmx.system._collections.PhysicalChannelCollection]:
            Indicates a collection that contains all the counter output
            physical channels available on the device.
        """
        return COPhysicalChannelCollection(self._name, self._interpreter)

    @property
    def di_lines(self):
        """
        List[nidaqmx.system._collections.PhysicalChannelCollection]:
            Indicates a collection that contains all the digital input
            lines available on the device.
        """
        return DILinesCollection(self._name, self._interpreter)

    @property
    def di_ports(self):
        """
        List[nidaqmx.system._collections.PhysicalChannelCollection]:
            Indicates a collection that contains all the digital input
            ports available on the device.
        """
        return DIPortsCollection(self._name, self._interpreter)

    @property
    def do_lines(self):
        """
        List[nidaqmx.system._collections.PhysicalChannelCollection]:
            Indicates a collection that contains all the digital output
            lines available on the device.
        """
        return DOLinesCollection(self._name, self._interpreter)

    @property
    def do_ports(self):
        """
        List[nidaqmx.system._collections.PhysicalChannelCollection]:
            Indicates a collection that contains all the digital output
            ports available on the device.
        """
        return DOPortsCollection(self._name, self._interpreter)

    # endregion

<%namespace name="property_template" file="/property_template.py.mako"/>\
%for attribute in attributes:
${property_template.script_property(attribute)}\
%endfor
\
<%namespace name="deprecated_template" file="/property_deprecated_template.py.mako"/>\
${deprecated_template.script_deprecated_property(attributes)}\
<%namespace name="function_template" file="/function_template.py.mako"/>\
%for function_object in functions:
${function_template.script_function(function_object)}
%endfor
\
    # region Network Device Functions

    @staticmethod
    def add_network_device(
            ip_address, device_name="", attempt_reservation=False,
            timeout=10.0, *, grpc_options=None):
        """
        Adds a Network cDAQ device to the system and, if specified,
        attempts to reserve it.

        Args:
            ip_address (str): Specifies the string containing the IP
                address (in dotted decimal notation) or hostname of the
                device to add to the system.
            device_name (Optional[str]): Indicates the name to assign to
                the device. If unspecified, NI-DAQmx chooses the device
                name.
            attempt_reservation (Optional[bool]): Indicates if a
                reservation should be attempted after the device is
                successfully added. By default, this parameter is set to
                False.
            timeout (Optional[float]): Specifies the time in seconds to
                wait for the device to respond before timing out.
            grpc_options (Optional[GrpcSessionOptions]): Specifies the 
                gRPC session options.
        Returns:
            nidaqmx.system.device.Device: 
            
            Specifies the object that represents the device this
            operation applied to.
        """
        device = Device("", grpc_options=grpc_options)
        
        device._name = device._interpreter.add_network_device(
            ip_address, device_name, attempt_reservation, timeout)

        return device

    def delete_network_device(self):
        """
        Deletes a Network DAQ device previously added to the host. If
        the device is reserved, it is unreserved before it is removed.
        """

        self._interpreter.delete_network_device(self._name)

    def reserve_network_device(self, override_reservation=None):
        """
        Reserves the Network DAQ device for the current host.
        Reservation is required to run NI-DAQmx tasks, and the device
        must be added in MAX before it can be reserved.

        Args:
            override_reservation (Optional[bool]): Indicates if an
                existing reservation on the device should be overridden
                by this reservation. By default, this parameter is set
                to false.
        """

        self._interpreter.reserve_network_device(self._name, override_reservation)

    def unreserve_network_device(self):
        """
        Unreserves or releases a Network DAQ device previously reserved
        by the host.
        """

        self._interpreter.unreserve_network_device(self._name)

    # endregion


class _DeviceAlternateConstructor(Device):
    """
    Provide an alternate constructor for the Device object.

    This is a private API used to instantiate a Device with an existing interpreter.
    """
    # Setting __slots__ avoids TypeError: __class__ assignment: 'Base' object layout differs from 'Derived'.
    __slots__ = []

    def __init__(self, name, interpreter):
        """
        Args:
            name: Specifies the name of the Device.
            interpreter: Specifies the interpreter instance.
            
        """
        self._name = name
        self._interpreter = interpreter

        # Use meta-programming to change the type of this object to Device,
        # so the user isn't confused when doing introspection.
        self.__class__ = Device