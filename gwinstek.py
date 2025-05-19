from pyvisa import ResourceManager, Resource
from typing import Literal
import logging


class AFG2125:
    def __init__(self, resource_name: str, resource_manager = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        if resource_manager is None:
            self._rm = ResourceManager()
        else:
            self._rm = resource_manager

        self._resource: Resource = self._rm.open_resource(resource_name)

    def close(self) -> None:
        self._resource.close()

    def query(self, command: str) -> str:
        self.logger.debug(f">>> {command}")
        response = self._resource.query(command).strip()
        self.logger.debug(f"<<< {response}")
        return response

    def write(self, command: str) -> None:
        self.logger.debug(f">>> {command}")
        self._resource.write(command)

    def identify(self) -> str:
        """
        Returns the function generator manufacturer model number, serial number,
        and firmware version in the following format:

        GW INSTEK,AFG-2025,SN:XXXXXXXX,Vm.mm
        """
        return self.query("*IDN?")
    
    def reset(self) -> None:
        """
        Resets the instrument to its factory default state
        """
        self.write("*RST")

    def clear(self) -> None:
        """
        Clears all the event registers, the error queue, and cancels
        and *OPC command
        """
        self.write("*CLS")

    def save(self, slot: int) -> None:
        """
        Saves a configuration or user-defined waveform to the given slot
        """
        self.write(f"*SAV {slot}")

    def recall(self, slot: int) -> None:
        """
        Recalls a configuration or user-defined waveform from the given slot
        """
        self.write(f"*RCL {slot}")

    def apply(
        self, 
        function: Literal["SIN", "SQU", "RAMP", "NOIS", "USER"], 
        frequency: Literal["MIN", "MAX", "DEF"] | float | str | None = None, 
        amplitude: Literal["MIN", "MAX", "DEF"] | float | str | None = None, 
        offset: Literal["MIN", "MAX", "DEF"] | float | str | None = None, 
    ) -> None:
        """
        Configures basic waveform parameters an immediately enable output
        """
        command = f"SOUR:APPL:{function}"
        if frequency is not None:
            command += f" {frequency}"
        if all(param is not None for param in [frequency, amplitude]):
            command += f",{amplitude}"
        if all(param is not None for param in [frequency, amplitude, offset]):
            command += f",{offset}"
        self.write(command)

    def set_function(self, function: Literal["SIN", "SQU", "RAMP", "NOIS", "USER"]) -> None:
        """
        Selects the output function. The USER parameter outputs an arbitrary waveform
        previously set. The previously set frequency, amplitude, and offset values
        are used automatically
        """
        self.write(f"SOUR:FUNC {function}")

    def get_function(self) -> Literal["SIN", "SQU", "RAMP", "NOIS", "USER"]:
        """
        Returns the current output function type
        """
        return self.query("SOUR:FUNC?")
    
    def set_frequency(self, frequency: Literal["MIN", "MAX"] | float | str):
        """
        Sets the output frequency in Hz. The maximum and minimum frequency depends
        on the function mode
        """
        self.write(f"SOUR:FREQ {frequency}")

    def get_frequency(self) -> float:
        """
        Returns the current output frequency setting in Hz
        """
        return float(self.query("SOUR:FREQ?"))
    
    def set_amplitude(self, amplitude: Literal["MIN", "MAX"] | float | str):
        """
        Sets the output amplitude. The maximum and minimum depends on the output
        termination. The default amplitude for all functions is 100 mVpp (50 ohm).
        The unit depends on the SOURCE:VOLTAGE:UNIT setting
        """
        self.write(f"SOUR:AMPL {amplitude}")

    def get_amplitude(self) -> float:
        """
        Returns the current output amplitude setting
        """
        return float(self.query("SOUR:AMPL?"))
    
    def set_offset(self, offset: Literal["MIN", "MAX"] | float | str):
        """
        Sets the DC offset for the current mode
        """
        self.write(f"SOUR:DCO {offset}")

    def get_offset(self) -> float:
        """
        Returns the DC offset for the current mode 
        """
        return float(self.query("SOUR:DCO?"))
    
    def set_duty_cycle(self, duty_cycle: Literal["MIN", "MAX"] | float):
        """
        Sets the duty cycle for square waves as a percentage
        """
        self.write(f"SOUR:SQU:DCYC {duty_cycle}")

    def get_duty_cycle(self) -> float:
        """
        Returns the duty cycle for square waves as a percentage
        """
        return float(self.query("SOUR:SQU:DCYC?"))
    
    def set_ramp_symmetry(self, symmetry: Literal["MIN", "MAX"] | float):
        """
        Sets the symmetry for ramp waves as a percentage
        """
        self.write(f"SOUR:RAMP:SYMM {symmetry}")

    def get_ramp_symmetry(self) -> float:
        """
        Returns the symmetry for ramp waves as a percentage
        """
        return float(self.query("SOUR:RAMP:SYMM?"))

    def set_output(self, state: Literal["ON", "OFF"]) -> None:
        """
        Enables/Disables the output
        """
        self.write(f"OUTP {state}")

    def get_output(self) -> float:
        """
        Returns the current output state
        """
        return float(self.query("OUTP?"))
    
    def set_output_load(self, load: Literal["DEF", "INF"]) -> None:
        """
        Sets the output termination load. The default output load is 50 ohm
        """
        self.write(f"OUTP:LOAD {load}")

    def get_output_load(self) -> Literal["DEF", "INF"]:
        """
        Returns the output termination load setting
        """
        return self.query("OUTP:LOAD?")
    
    def set_voltage_unit(self, unit: Literal["VPP", "VRMS", "DBM"]) -> None:
        """
        Sets the output amplitude units
        """
        self.write(f"SOUR:VOLT:UNIT {unit}")

    def get_voltage_unit(self) -> Literal["VPP", "VRMS", "DBM"]:
        """
        Returns the output amplitude units
        """
        return self.query("SOUR:VOLT:UNIT?")
    
    def set_amplitude_modulation(
        self,
        state: Literal["ON", "OFF"] = "OFF",
        source: Literal["INT", "EXT"] = "INT",
        function: Literal["SIN", "SQU", "RAMP"] = "SIN",
        frequency: Literal["MIN", "MAX"] | float = 100.0,
        depth: Literal["MIN", "MAX"] | float = 100.0,
    ) -> None:
        """
        Configures amplitude modulation mode. Use the apply command to configure the 
        carrier waveform first
        """
        self.write(f"SOUR:AM:STAT {state}")
        if state == "OFF":
            return
        
        self.write(f"SOUR:AM:SOUR {source}")
        if source == "INT":
            self.write(f"SOUR:AM:INT:FUNC {function}")
            self.write(f"SOUR:AM:INT:FREQ {frequency}")

        self.write(f"SOUR:AM:DEPT {depth}")

    def set_frequency_modulation(
        self,
        state: Literal["ON", "OFF"] = "OFF",
        source: Literal["INT", "EXT"] = "INT",
        function: Literal["SIN", "SQU", "RAMP"] = "SIN",
        frequency: Literal["MIN", "MAX"] | float = 100.0,
        deviation: Literal["MIN", "MAX"] | float = 100.0,
    ) -> None:
        """
        Configures frequency modulation mode. Use the apply command to configure the 
        carrier waveform first
        """
        self.write(f"SOUR:FM:STAT {state}")
        if state == "OFF":
            return
        
        self.write(f"SOUR:FM:SOUR {source}")
        if source == "INT":
            self.write(f"SOUR:FM:INT:FUNC {function}")
            self.write(f"SOUR:FM:INT:FREQ {frequency}")

        self.write(f"SOUR:FM:DEV {deviation}")
    
    def set_frequency_sweep(
        self,
        state: Literal["ON", "OFF"] = "OFF",
        start: Literal["MIN", "MAX"] | float = 10.0,
        stop: Literal["MIN", "MAX"] | float = 10000.0,
        spacing: Literal["LIN", "LOG"] = "LIN",
        rate: Literal["MIN", "MAX"] | float = 1.0,
        source: Literal["IMM", "EXT"] = "IMM",
    ) -> None:
        """
        Configures frequency sweep mode. Use the apply command to configure the 
        base waveform first
        """
        self.write(f"SOUR:SWE:STAT {state}")
        if state == "OFF":
            return

        self.write(f"SOUR:FREQ:STAR {start}")
        self.write(f"SOUR:FREQ:STOP {stop}")
        self.write(f"SOUR:SWE:SPAC {spacing}")
        self.write(f"SOUR:SWE:RATE {rate}")
        self.write(f"SOUR:SWE:SOUR {source}")

    def set_arb_data(self, data: list, slot: int = 10) -> None:
        """
        Configures an arbitrary waveform cycle and saves it to the designated slot
        """
        assert len(data) >= 1 and len(data) <= 4096
        assert slot in list(range(10, 20))

        max_val = max(abs(x) for x in data)
        if max_val == 0:
            return [0.0] * len(data)  # Avoid division by zero
        scale = 511.0 / max_val
        data_str = ",".join([str(round(x * scale)) for x in data])

        self.write(f"DATA:DAC VOLATILE,0,{data_str}")
        self.save(slot)
