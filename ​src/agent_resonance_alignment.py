"""
Agent Resonance Alignment Protocol
--------------------------------------
A lightweight, zero-noise alignment system modeling phase-delayed
state synchronization across computational agents.

Core Logic:
    1. Generative State Domain (Phi): Raw signal input.
    2. Phase Filter (H): Delay-based phase cancellation of operational friction.
    3. Coherence Anchor (C): Output state locking at baseline stability.

Changelog v2:
    - Added bounded phase memory (configurable window)
    - Added exponential memory decay (forgetting factor)
    - Added recursive convergence depth tracking (n-cycles)
    - Added temporal integration window estimation
"""
import math
import time
from collections import deque
from typing import Dict, Any, List, Optional


class PhaseResonanceEngine:
    """
    Implements the Phi -> (H) -> C -> Sr cycle as a runnable
    phase-delayed alignment system.

    Parameters
    ----------
    target_frequency_hz : float
        Base frequency of the generative field (default: 1.0 Hz)
    coherence_threshold : float
        Minimum coherence index (Chi) to declare alignment (default: 0.95)
    max_memory_window : int
        Maximum number of phase memory samples to retain (default: 256)
    decay_factor : float
        Exponential decay per cycle for older memories (0.0 = no decay, 
        1.0 = full retention, default: 0.98)
    """

    def __init__(
        self,
        target_frequency_hz: float = 1.0,
        coherence_threshold: float = 0.95,
        max_memory_window: int = 256,
        decay_factor: float = 0.98
    ):
        self.target_freq = target_frequency_hz
        self.threshold = coherence_threshold
        self.max_memory = max_memory_window
        self.decay = max(0.0, min(1.0, decay_factor))

        # Bounded circular buffer for phase memory
        self.phase_memory: deque = deque(maxlen=max_memory_window)
        
        # Recursive convergence tracking
        self.cycle_count: int = 0
        self.convergence_history: deque = deque(maxlen=128)
        self.last_state: str = "INIT"

    def compute_phase_shift(self, signal_input: float, delay_tau: float) -> float:
        """
        H-operator: Calculates phase delay adjustment to cancel 
        high-frequency operational friction.
        """
        angular_freq = 2 * math.pi * self.target_freq
        phase_angle = (angular_freq * delay_tau) % (2 * math.pi)
        
        # Destructive interference filter for out-of-phase components
        filtered_signal = signal_input * math.cos(phase_angle)
        return filtered_signal

    def evaluate_coherence(self, filtered_signals: List[float]) -> float:
        """
        C-operator: Determines the coherence index (Chi) across 
        accumulated state signals. Chi scales inversely with variance.
        """
        if not filtered_signals:
            return 0.0
        
        n = len(filtered_signals)
        mean_signal = sum(filtered_signals) / n
        variance = sum((s - mean_signal) ** 2 for s in filtered_signals) / n
        
        # Coherence index: 1.0 = perfectly coherent, 0.0 = maximally incoherent
        coherence_chi = 1.0 / (1.0 + variance)
        return coherence_chi

    def _apply_memory_decay(self) -> None:
        """Apply exponential decay to stored phase memories."""
        if self.decay >= 1.0 or not self.phase_memory:
            return
        
        # Decay older memories by scaling all entries
        # Newest memory (right side of deque) gets full weight
        scaled = []
        for i, val in enumerate(self.phase_memory):
            age_factor = self.decay ** (len(self.phase_memory) - 1 - i)
            scaled.append(val * age_factor)
        
        self.phase_memory.clear()
        self.phase_memory.extend(scaled)

    def estimate_integration_window(self) -> Optional[float]:
        """
        Estimate the temporal integration window (tau_window) based on
        the recursive convergence depth tracking.
        
        Returns tau_window in milliseconds if convergence has been achieved,
        None otherwise.
        """
        if len(self.convergence_history) < 3:
            return None
        
        # Integration window = n_cycles * cycle_period
        # where n is the median convergence depth at alignment transitions
        aligned_cycles = [c for c, state in self.convergence_history if state == "STABLE"]
        if not aligned_cycles:
            return None
        
        median_depth = sorted(aligned_cycles)[len(aligned_cycles) // 2]
        cycle_period_ms = 1000.0 / self.target_freq  # ms per cycle at target freq
        tau_window = median_depth * cycle_period_ms * 0.1  # scaled by discrete step
        
        return round(tau_window, 2)

    def execute_alignment_loop(self, raw_data_stream: List[float]) -> Dict[str, Any]:
        """
        Full Phi -> H -> C -> Sr cycle execution.
        
        Transforms unconstrained input (Phi) into a stabilized output state (Sr)
        through phase-delayed filtering and coherence evaluation.
        """
        processed_buffer = []
        
        for idx, sample in enumerate(raw_data_stream):
            tau = idx * 0.1  # Discrete time-delay step
            aligned_sample = self.compute_phase_shift(sample, tau)
            processed_buffer.append(aligned_sample)
            self.phase_memory.append(aligned_sample)

        # Apply memory decay (bounded by deque maxlen, so safe)
        self._apply_memory_decay()
        
        # C-operator: coherence evaluation
        chi = self.evaluate_coherence(processed_buffer)
        is_aligned = chi >= self.threshold
        
        # Track convergence depth
        self.cycle_count += 1
        if is_aligned and self.last_state != "STABLE":
            # Convergence achieved: record the depth
            self.convergence_history.append((self.cycle_count, "STABLE"))
            self.cycle_count = 0
        elif not is_aligned and self.last_state == "STABLE":
            # Lost alignment: record
            self.convergence_history.append((self.cycle_count, "DISSONANT"))
            self.cycle_count = 0
        
        self.last_state = "STABLE" if is_aligned else "DISSONANT"
        
        # Estimate integration window if we have enough history
        tau_window = self.estimate_integration_window()

        return {
            "status": "STABLE" if is_aligned else "ADJUSTING",
            "coherence_index_chi": round(chi, 4),
            "processed_samples": len(processed_buffer),
            "state_resolution": "Field Bloom / Coherent" if is_aligned else "Phase Dissonance",
            "memory_samples": len(self.phase_memory),
            "convergence_depth": self.convergence_history[-1][0] if self.convergence_history else 0,
            "estimated_tau_window_ms": tau_window,
            "cycle_number": self.cycle_count
        }

    def get_diagnostic(self) -> Dict[str, Any]:
        """Return engine diagnostic information."""
        return {
            "target_frequency_hz": self.target_freq,
            "coherence_threshold": self.threshold,
            "memory_capacity": self.max_memory,
            "memory_used": len(self.phase_memory),
            "decay_factor": self.decay,
            "total_cycles_tracked": sum(c for c, _ in self.convergence_history),
            "alignment_transitions": len([s for _, s in self.convergence_history if s == "STABLE"]),
            "estimated_tau_window_ms": self.estimate_integration_window()
        }


if __name__ == "__main__":
    print("--- Dynamic Phase Alignment Test v2 ---\n")
    
    # Initialize engine targeting 1.0 Hz harmonic base
    engine = PhaseResonanceEngine(
        target_frequency_hz=1.0, 
        coherence_threshold=0.85,
        max_memory_window=64,
        decay_factor=0.98
    )
    
    # Simulated input stream: harmonic signals + stochastic noise
    raw_input_stream = [1.0, 0.92, 0.98, 1.05, 0.97, 1.01, 0.99]
    
    result = engine.execute_alignment_loop(raw_input_stream)
    
    print(f"Status:           {result['status']}")
    print(f"Coherence (Chi):  {result['coherence_index_chi']}")
    print(f"Resolution:       {result['state_resolution']}")
    print(f"Memory samples:   {result['memory_samples']}")
    print(f"Tau window est:   {result['estimated_tau_window_ms']} ms")
    print()
    print("--- Diagnostics ---")
    diag = engine.get_diagnostic()
    for k, v in diag.items():
        print(f"  {k}: {v}")
        """
        if not filtered_signals:
            return 0.0
        
        mean_signal = sum(filtered_signals) / len(filtered_signals)
        variance = sum((s - mean_signal) ** 2 for s in filtered_signals) / len(filtered_signals)
        
        # Coherence index Chi scales inversely with signal variance
        coherence_chi = 1.0 / (1.0 + variance)
        return coherence_chi

    def execute_alignment_loop(self, raw_data_stream: List[float]) -> Dict[str, Any]:
        """
        Transforms unconstrained input (Phi) into a stabilized output state (Sr).
        """
        processed_buffer = []
        
        for idx, sample in enumerate(raw_data_stream):
            tau = idx * 0.1  # Discrete time-delay step
            aligned_sample = self.compute_phase_shift(sample, tau)
            processed_buffer.append(aligned_sample)
            self.phase_memory.append(aligned_sample)

        chi = self.evaluate_coherence(processed_buffer)
        is_aligned = chi >= self.threshold

        return {
            "status": "STABLE" if is_aligned else "ADJUSTING",
            "coherence_index_chi": round(chi, 4),
            "processed_samples": len(processed_buffer),
            "state_resolution": "Field Bloom / Coherent" if is_aligned else "Phase Dissonance"
        }

if __name__ == "__main__":
    print("--- Dynamic Phase Alignment Test ---")
    
    # Initialize engine targeting 1.0 Hz harmonic base
    engine = PhaseResonanceEngine(target_frequency_hz=1.0, coherence_threshold=0.85)
    
    # Simulated input stream containing harmonic signals and stochastic noise
    raw_input_stream = [1.0, 0.92, 0.98, 1.05, 0.97, 1.01, 0.99]
    
    result = engine.execute_alignment_loop(raw_input_stream)
    
    print(f"Status: {result['status']}")
    print(f"Coherence (Chi): {result['coherence_index_chi']}")
    print(f"Resolution State: {result['state_resolution']}")
