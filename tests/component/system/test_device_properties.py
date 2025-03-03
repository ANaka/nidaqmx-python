import pytest

from nidaqmx import DaqError
from nidaqmx.constants import BusType, TriggerUsage
from nidaqmx.error_codes import DAQmxErrors
from nidaqmx.system import Device


def test___constructed_device___get_property___returns_value(init_kwargs):
    device = Device("bridgeTester", **init_kwargs)

    assert device.product_type == "PXIe-4331"


def test___nonexistent_device___get_property___raises_invalid_device_id(init_kwargs):
    device = Device("NonexistentDevice", **init_kwargs)

    with pytest.raises(DaqError) as exc_info:
        _ = device.product_type

    assert exc_info.value.error_code == DAQmxErrors.INVALID_DEVICE_ID


@pytest.mark.device_name("bridgeTester")
def test___device___bool_property___returns_value(device):
    # The PXIe-4331 supports analog triggering
    assert device.anlg_trig_supported


@pytest.mark.device_name("bridgeTester")
def test___device___float_property___returns_value(device):
    # The ai max single channel rate of the NI PXIe-4331 device is 102400.0
    assert device.ai_max_single_chan_rate == 102400.0


@pytest.mark.device_name("bridgeTester")
def test___device___uint_property___returns_value(device):
    assert device.product_num == 0x74A9C4C4


@pytest.mark.device_name("bridgeTester")
def test___device___string_property___returns_value(device):
    assert device.product_type == "PXIe-4331"


@pytest.mark.device_name("bridgeTester")
def test___device___enum_property___returns_value(device):
    assert device.bus_type == BusType.PXIE


@pytest.mark.device_name("bridgeTester")
def test___device___list_of_float_property___returns_value(device):
    ai_bridge_ranges = device.ai_bridge_rngs

    assert isinstance(ai_bridge_ranges, list)
    assert ai_bridge_ranges == [-0.025, 0.025, -0.1, 0.1]


@pytest.mark.grpc_xfail(
    reason="Requires NI gRPC Device Server version 2.2 or later",
    raises=DaqError,
)
@pytest.mark.device_name("bridgeTester")
def test___device___list_of_enum_property___returns_value(device):
    ai_trigger_usage = device.ai_trig_usage

    assert isinstance(ai_trigger_usage, list)
    assert ai_trigger_usage == [TriggerUsage.REFERENCE, TriggerUsage.START]


@pytest.mark.device_name("bridgeTester")
def test___device___list_of_uint_property___returns_value(device):
    accessory_product_numbers = device.accessory_product_nums

    assert isinstance(accessory_product_numbers, list)
    assert accessory_product_numbers == [0x7992]


@pytest.mark.device_name("bridgeTester")
def test___device___get_deprecated_properties___reports_warnings(device):
    with pytest.deprecated_call():
        assert device.is_simulated == device.dev_is_simulated
    with pytest.deprecated_call():
        assert device.serial_num == device.dev_serial_num
    with pytest.deprecated_call():
        assert device.hwteds_supported == device.tedshwteds_supported


@pytest.mark.device_name("tsChassisTester")
def test___chassis___get_modules___returns_modules(device: Device):
    modules = device.chassis_module_devices

    assert [mod.name for mod in modules] == ["tsPowerTester1", "tsPowerTester2", "tsVoltageTester1"]


@pytest.mark.device_name("tsChassisTester")
def test___chassis___get_modules___shared_interpreter(device: Device):
    modules = device.chassis_module_devices

    assert all(mod._interpreter is device._interpreter for mod in modules)


@pytest.mark.device_name("tsVoltageTester1")
def test___module___get_chassis___returns_chassis(device: Device):
    chassis = device.compact_daq_chassis_device

    assert chassis.name == "tsChassisTester"


@pytest.mark.device_name("tsVoltageTester1")
def test___module___get_chassis___shared_interpreter(device: Device):
    chassis = device.compact_daq_chassis_device

    assert chassis._interpreter is device._interpreter
