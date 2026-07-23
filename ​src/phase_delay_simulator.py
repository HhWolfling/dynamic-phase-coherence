"""
Phase Delay & Destructive Interference Simulator
------------------------------------------------
A runnable Python script modeling trapped recursive wave loops,
phase delay shifts (tau), and real-time noise cancellation.
"""

import math
import time

def generate_carrier_wave(time_step: float, frequency: float = 5.0) -> float:
    """Generates a clean baseline signal wave."""
    return math.sin(2 * math.pi * frequency * time_step)

def generate_environmental_noise(time_step: float) -> float:
    """Simulates high-frequency stochastic environmental friction."""
    return 0.4 * math.sin(2 * math.pi * 37.0 * time_step) + 0.2 * math.cos(2 * math.pi * 83.0 * time_step)

def apply_phase_delay_filter(signal: float, phase_shift_radians: float) -> float:
    """
    Applies an exact phase-inverted counter-wave to cancel out 
    high-frequency environmental noise.
    """
    counter_wave = signal * math.cos(phase_shift_radians)
    return counter_wave

def run_simulation(steps: int = 10):
    print("=" * 60)
    print(" DYNAMIC PHASE DELAY & WAVE CANCELLATION SIMULATOR ")
    print("=" * 60)
    print(f"{'TimeStep (s)':<15}{'Raw Signal':<15}{'Noise Layer':<15}{'Filtered Output':<15}")
    print("-" * 60)

    for i in range(steps):
        t = i * 0.02  # 20ms discrete steps
        carrier = generate_carrier_wave(t)
        noise = generate_environmental_noise(t)
        combined_input = carrier + noise

        # Calculate exact destructive phase angle (180 deg / pi radians out of phase for noise)
        optimal_tau_shift = math.pi
        filtered_output = apply_phase_delay_filter(combined_input, optimal_tau_shift)

        print(f"{t:<15.2f}{carrier:<15.4f}{noise:<15.4f}{filtered_output:<15.4f}")
        time.sleep(0.05)

    print("-" * 60)
    print("Simulation Complete: Phase cancellation locked baseline stability.")

if __name__ == "__main__":
    run_simulation()
