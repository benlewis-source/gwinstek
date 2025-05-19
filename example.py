"""
Configures an arbitrary waveform
"""
from .gwinstek import AFG2125
import numpy as np


if __name__ == "__main__":
    # Create a sine wave cycle
    sine = np.sin(np.linspace(0, 2 * np.pi, 4096, endpoint=False))

    afg = AFG2125("ASRL9::INSTR")
    afg.set_arb_data(sine, slot=10)
    afg.apply(
        function="USER",
        frequency=1000,
        amplitude=1.0,
        offset=0.0
    )
    afg.close()
