import struct

import pytest

from climb.runner import child

OWN = 4000
ENTRY = 3999

ALLOWED, REFUSED, KILLED = "allowed", "refused", "killed"


def verdict(machine: str, name: str, *args: int, nr: int | None = None, arch: int | None = None):
    """The program run as the kernel runs it, over one call's `seccomp_data`."""
    calls = child.SYSCALLS[machine]
    padded = [*args, 0, 0, 0, 0, 0, 0][:6]
    data = struct.pack(
        "<iIQ6Q",
        calls[name] if nr is None else nr,
        calls["audit"] if arch is None else arch,
        0,
        *(value & 0xFFFFFFFFFFFFFFFF for value in padded),
    )
    program = child.seccomp_program(machine, OWN)
    at, accumulator = 0, 0
    while True:
        code, jt, jf, k = program[at]
        if code == child.BPF_LOAD:
            (accumulator,) = struct.unpack_from("<I", data, k)
            at += 1
        elif code in (child.BPF_EQUAL, child.BPF_AT_LEAST):
            hit = accumulator == k if code == child.BPF_EQUAL else accumulator >= k
            at += 1 + (jt if hit else jf)
        else:
            assert code == child.BPF_RETURN
            return {child.RET_ALLOW: ALLOWED, child.RET_REFUSE: REFUSED}.get(k, KILLED)


MACHINES = pytest.mark.parametrize("machine", sorted(child.SYSCALLS))


@MACHINES
def test_a_case_signals_its_own_group_and_nothing_else(machine: str):
    """The entry process and the container's init are outside the case's
    group, and `kill(-1)` reaches both."""
    assert verdict(machine, "kill", OWN, 9) == ALLOWED
    assert verdict(machine, "kill", 0, 15) == ALLOWED
    assert verdict(machine, "kill", -OWN, 9) == ALLOWED
    assert verdict(machine, "kill", ENTRY, 9) == REFUSED
    assert verdict(machine, "kill", 1, 9) == REFUSED
    assert verdict(machine, "kill", -1, 9) == REFUSED
    assert verdict(machine, "tgkill", OWN, OWN, 6) == ALLOWED
    assert verdict(machine, "tgkill", ENTRY, ENTRY, 19) == REFUSED
    assert verdict(machine, "tkill", ENTRY, 9) == REFUSED


@MACHINES
def test_a_pid_is_read_from_its_low_32_bits(machine: str):
    """The kernel truncates a pid_t register, so garbage above it changes
    nothing."""
    assert verdict(machine, "kill", (1 << 32) | ENTRY, 9) == REFUSED
    assert verdict(machine, "kill", (1 << 32) | OWN, 9) == ALLOWED


@MACHINES
def test_tracing_and_aiming_sigio_at_another_process_are_refused(machine: str):
    for name in ("ptrace", "process_vm_writev", "pidfd_send_signal"):
        assert verdict(machine, name, 16, ENTRY) == REFUSED
    assert verdict(machine, "fcntl", 3, child.F_SETOWN, ENTRY) == REFUSED
    assert verdict(machine, "ioctl", 3, child.FIOSETOWN, ENTRY) == REFUSED
    assert verdict(machine, "fcntl", 3, 3) == ALLOWED  # F_GETFL
    assert verdict(machine, "ioctl", 3, 0x5401) == ALLOWED  # TCGETS


@MACHINES
def test_every_other_call_is_allowed(machine: str):
    assert verdict(machine, "kill", nr=39) == ALLOWED


@MACHINES
def test_a_call_from_another_architecture_kills_the_case(machine: str):
    """Another architecture's table numbers the calls differently, so the
    filter's numbers say nothing there."""
    assert verdict(machine, "kill", ENTRY, 9, arch=0x40000003) == KILLED


def test_an_x32_call_kills_the_case():
    assert verdict("x86_64", "kill", ENTRY, 9, nr=child.X32_BIT | 62) == KILLED
