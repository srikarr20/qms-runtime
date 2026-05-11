"""
Quantum Control System logic for QMCTB-01
"""

from enum import Enum, auto
from dataclasses import dataclass


class RunStatus(Enum):
    ACCEPT = auto()
    CONTINUE = auto()
    REJECT = auto()


class FailureClass(Enum):
    NONE = auto()
    LOW_VISIBILITY = auto()
    INSUFFICIENT_FRAMES = auto()


class DetectorMode(Enum):
    PRESERVE = auto()
    DESTROY = auto()


@dataclass
class Diagnostics:
    V_preserve: float
    sigma_preserve: float
    V_destroy: float
    sigma_destroy: float
    N_frames: int
    N_max: int
    visibility_threshold: float


@dataclass
class QCSDecision:
    run_status: RunStatus
    failure_class: FailureClass
    next_frame_budget: int
    detector_mode: DetectorMode
    message: str


def qcs_decide(d: Diagnostics, detector_mode: DetectorMode) -> QCSDecision:

    if d.V_preserve >= d.visibility_threshold:
        return QCSDecision(
            run_status=RunStatus.ACCEPT,
            failure_class=FailureClass.NONE,
            next_frame_budget=0,
            detector_mode=DetectorMode.PRESERVE,
            message="Benchmark PASSED: interference preserved and validated."
        )

    if d.N_frames < d.N_max:
        return QCSDecision(
            run_status=RunStatus.CONTINUE,
            failure_class=FailureClass.INSUFFICIENT_FRAMES,
            next_frame_budget=min(d.N_frames * 2, d.N_max),
            detector_mode=detector_mode,
            message="Insufficient confidence. Increasing frame budget."
        )

    return QCSDecision(
        run_status=RunStatus.REJECT,
        failure_class=FailureClass.LOW_VISIBILITY,
        next_frame_budget=0,
        detector_mode=DetectorMode.DESTROY,
        message="Benchmark FAILED: interference not preserved."
    )

