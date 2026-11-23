"""One solution, one case, and what the call produced.

Imports nothing from the package: the broker sends this script to a run's
container, and `main` is that container's entry process.
"""

import contextlib
import ctypes
import json
import linecache
import os
import resource
import select
import signal
import sys
import time
import traceback
from types import FrameType
from typing import Any

RETURNED = "returned"
TIMEOUT = "timeout"
CRASHED = "crashed"

# the filename the solution is compiled under, and the frames a crash report
# keeps
SOLUTION = "<solution>"

# slack on the entry's own timer, beyond the cap the child enforces. The local
# runner's STARTUP_MS, which this script cannot import
SLACK_MS = 2000

# a case's own address space, under the container's memory limit. A case that
# exhausts memory then raises in its own child, where the container's limit
# alone has the host kill the container and every later case with it
CASE_MEMORY_BYTES = 320 << 20

# a case's own processes, under the container's process limit, for the same
# reason: gVisor backs each process a case starts with a host process, so a
# case reaching the container's limit ends the sandbox itself
CASE_PROCESSES = 32

# set on a run's container by the broker. The process limit counts every
# process of a user, so it holds only where that user owns the run alone
SANDBOX = "CLIMB_SANDBOX"

# the system calls by which a case reaches a process outside its own: a signal,
# a trace, another's memory, and a SIGIO aimed by F_SETOWN or FIOSETOWN. Each
# number is per architecture, with the audit value the filter checks first
SYSCALLS = {
    "x86_64": {
        "audit": 0xC000003E,
        "kill": 62, "tkill": 200, "tgkill": 234, "rt_sigqueueinfo": 129,
        "rt_tgsigqueueinfo": 297, "pidfd_send_signal": 424, "ptrace": 101,
        "process_vm_readv": 310, "process_vm_writev": 311, "fcntl": 72, "ioctl": 16,
    },
    "aarch64": {
        "audit": 0xC00000B7,
        "kill": 129, "tkill": 130, "tgkill": 131, "rt_sigqueueinfo": 138,
        "rt_tgsigqueueinfo": 240, "pidfd_send_signal": 424, "ptrace": 117,
        "process_vm_readv": 270, "process_vm_writev": 271, "fcntl": 25, "ioctl": 29,
    },
}  # fmt: skip
F_SETOWN, F_SETOWN_EX = 8, 15
FIOSETOWN, SIOCSPGRP = 0x8901, 0x8902
PR_SET_NO_NEW_PRIVS, PR_SET_SECCOMP, SECCOMP_MODE_FILTER = 38, 22, 2
# classic BPF's opcodes, and the offsets into `struct seccomp_data`
BPF_LOAD, BPF_EQUAL, BPF_AT_LEAST, BPF_RETURN = 0x20, 0x15, 0x35, 0x06
NR_OFFSET, ARCH_OFFSET, ARGS_OFFSET = 0, 4, 16
X32_BIT = 0x40000000
# allow, fail with EPERM, and kill the process: a call from another
# architecture's table could reach what the numbers above refuse
RET_ALLOW, RET_REFUSE, RET_KILL = 0x7FFF0000, 0x00050001, 0x80000000


class Expired(Exception):
    """Its own exception, so a solution catching `Exception` cannot swallow the
    cap."""


def encode(value: object) -> str:
    # must stay the encoder `encoding.as_json` uses, or a return would be
    # decided differently by where it ran
    return json.dumps(value, sort_keys=True)


def execute(code: str, args: list[Any], cap_ms: int, repeats: int = 1) -> dict[str, Any]:
    # the cap times the `solve` calls alone; interpreter start and the module's
    # top level are the parent timer's to catch
    try:
        compiled = compile(code, SOLUTION, "exec")
        exec(compiled, {"__name__": "__solution__"})
    except BaseException as error:
        return crashed(None, described(error, code))

    signal.signal(signal.SIGALRM, _expire)
    signal.setitimer(signal.ITIMER_REAL, cap_ms / 1000)
    elapsed = 0.0
    value = None
    raised: BaseException | None = None
    try:
        for _ in range(repeats):
            # a fresh module per call, so a memo left in a global cannot answer
            # the next one. It costs microseconds and is outside the timing,
            # as the module's top level is on a single call
            namespace: dict[str, Any] = {"__name__": "__solution__"}
            exec(compiled, namespace)
            solve = namespace["solve"]
            started = time.perf_counter()
            value = solve(*args)
            elapsed += time.perf_counter() - started
    except Expired:
        return {"outcome": TIMEOUT, "value": None, "elapsed_ms": round(elapsed * 1000)}
    except BaseException as error:
        raised = error
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)

    measured = round(elapsed * 1000)
    # reported once the timer is off: formatting a deep traceback outlasts a
    # short cap, and the cap firing inside the report left no result at all
    if raised is not None:
        return crashed(measured, described(raised, code))
    try:
        encoded = encode(value)
    except TypeError, ValueError:
        # a return JSON cannot encode is the solution's fault, not a wrong
        # answer
        kind = type(value).__name__
        return crashed(measured, f"solve returned a {kind}, which JSON cannot encode")
    return {"outcome": RETURNED, "value": encoded, "elapsed_ms": measured}


def crashed(elapsed_ms: int | None, error: str) -> dict[str, Any]:
    return {"outcome": CRASHED, "value": None, "elapsed_ms": elapsed_ms, "error": error}


def described(error: BaseException, code: str) -> str:
    """The exception as a traceback prints it, over the solution's own frames.
    The child's frames name no line the solver wrote."""
    # a compiled string has no file to read its lines back from
    linecache.cache[SOLUTION] = (len(code), None, code.splitlines(keepends=True), SOLUTION)
    report = traceback.TracebackException.from_exception(error)
    report.stack = traceback.StackSummary.from_list(
        [frame for frame in report.stack if frame.filename == SOLUTION]
    )
    return "".join(report.format())


def _expire(_signum: int, _frame: FrameType | None) -> None:
    raise Expired


def answered(code: str, args: list[Any], cap_ms: int, repeats: int) -> dict[str, Any]:
    """`execute`, so a child always has a result to write: the cap firing in
    the window before its timer was disarmed is a timeout, and anything else
    escaping the report, such as memory spent on a deep traceback, a crash."""
    try:
        return execute(code, args, cap_ms, repeats)
    except Expired:
        signal.setitimer(signal.ITIMER_REAL, 0)
        return {"outcome": TIMEOUT, "value": None, "elapsed_ms": None}
    except BaseException as error:
        signal.setitimer(signal.ITIMER_REAL, 0)
        return crashed(None, f"{type(error).__name__} while reporting the crash")


def case(code: str, args: list[Any], cap_ms: int, repeats: int, result_path: str) -> None:
    """One case in a child the local runner forked for it."""
    _isolate()
    result = answered(code, args, cap_ms, repeats)
    with open(result_path, "w") as handle:
        json.dump(result, handle)


def _isolate() -> None:
    """Its own session, so a solution's own children die with it, and no
    stream the solution can print to."""
    os.setsid()
    silent = os.open(os.devnull, os.O_RDWR)
    for stream in (0, 1, 2):
        os.dup2(silent, stream)


# run once before a run's first case and thrown away: the first case after a
# container boots otherwise runs on pages and caches gVisor has not yet touched
WARM_UP = "def solve():\n    return 0\n"


def main() -> None:
    """A whole run from standard input, one result line per case on standard
    output."""
    request = json.loads(sys.stdin.read())
    cases: list[list[Any]] = request["args"]
    counts: list[int] = request.get("repeats") or [1] * len(cases)
    if cases:
        forked(WARM_UP, [], request["cap_ms"], 1)
    for args, repeats in zip(cases, counts, strict=True):
        result = forked(request["code"], args, request["cap_ms"], repeats)
        sys.stdout.write(json.dumps(result) + "\n")
        sys.stdout.flush()
        # never at a returned value, however wrong: nothing here knows what a
        # case expects
        if request.get("stop_early") and result["outcome"] != RETURNED:
            break


def forked(code: str, args: list[Any], cap_ms: int, repeats: int) -> dict[str, Any]:
    """One case in a child of its own, its result read back over a pipe."""
    read, write = os.pipe()
    pid = os.fork()
    if pid == 0:
        try:
            os.close(read)
            _isolate()
            _limit()
            if sys.platform == "linux":
                _confine(os.getpid())
            result = answered(code, args, cap_ms, repeats)
            with os.fdopen(write, "w") as channel:
                channel.write(json.dumps(result) + "\n")
        finally:
            # never back into the entry's loop, whatever raised
            os._exit(0)

    os.close(write)
    try:
        line = _line(read, time.monotonic() + (cap_ms + SLACK_MS) / 1000)
    finally:
        os.close(read)
        # on every path: what the solution spawned outlives a child that
        # reported, and holds the pipe open besides
        for kill in (os.killpg, os.kill):
            with contextlib.suppress(ProcessLookupError, PermissionError):
                kill(pid, signal.SIGKILL)
        _, status = os.waitpid(pid, 0)

    if line is None:
        return {"outcome": TIMEOUT, "value": None, "elapsed_ms": None}
    if line:
        return json.loads(line)
    exitcode = os.waitstatus_to_exitcode(status)
    if exitcode < 0:
        return crashed(None, f"killed by signal {-exitcode}")
    raise RuntimeError(f"the child wrote no result and exited {exitcode}")


def _limit() -> None:
    limits = [(resource.RLIMIT_AS, CASE_MEMORY_BYTES)]
    if os.environ.get(SANDBOX):
        limits.append((resource.RLIMIT_NPROC, CASE_PROCESSES))
    # suppressed where the platform refuses a limit, which leaves the
    # container's own limits as they were
    for kind, most in limits:
        with contextlib.suppress(OSError, ValueError):
            resource.setrlimit(kind, (most, most))


def _confine(own: int) -> None:
    """Installs `seccomp_program`, which every process the solution starts
    inherits. A refusal raises, so no case runs unconfined."""
    resolved = seccomp_program(os.uname().machine, own)

    class Instruction(ctypes.Structure):
        _fields_ = [
            ("code", ctypes.c_ushort),
            ("jt", ctypes.c_ubyte),
            ("jf", ctypes.c_ubyte),
            ("k", ctypes.c_uint),
        ]

    class Program(ctypes.Structure):
        _fields_ = [("len", ctypes.c_ushort), ("filter", ctypes.POINTER(Instruction))]

    program = Program(len(resolved), (Instruction * len(resolved))(*resolved))
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) or libc.prctl(
        PR_SET_SECCOMP, SECCOMP_MODE_FILTER, ctypes.byref(program), 0, 0
    ):
        raise OSError(ctypes.get_errno(), "the kernel refused the case's seccomp filter")


def seccomp_program(machine: str, own: int) -> list[tuple[int, int, int, int]]:
    """A classic BPF program refusing each call that reaches a process outside
    the case's own process group, as `(code, jt, jf, k)`."""
    calls = SYSCALLS[machine]
    # by the target's id: kill(0) and kill(-own) are the case's own group,
    # since `_isolate` made the case a session leader
    guarded = {
        "kill": [0, own, -own],
        "tkill": [own],
        "tgkill": [own],
        "rt_sigqueueinfo": [own],
        "rt_tgsigqueueinfo": [own],
    }
    refused = ("pidfd_send_signal", "ptrace", "process_vm_readv", "process_vm_writev")
    # by the command: each aims SIGIO, whose default action ends a process
    commands = {"fcntl": [F_SETOWN, F_SETOWN_EX], "ioctl": [FIOSETOWN, SIOCSPGRP]}

    program: list[tuple[int, int, str | None, str | None]] = []
    labels: dict[str, int] = {}

    def op(code: int, k: int, yes: str | None = None, no: str | None = None) -> None:
        program.append((code, k, yes, no))

    op(BPF_LOAD, ARCH_OFFSET)
    op(BPF_EQUAL, calls["audit"], no="kill process")
    op(BPF_LOAD, NR_OFFSET)
    if machine == "x86_64":
        # the x32 numbers reach the same calls under numbers of their own
        op(BPF_AT_LEAST, X32_BIT, yes="kill process")
    for name in [*guarded, *commands]:
        op(BPF_EQUAL, calls[name], yes=name)
    for name in refused:
        op(BPF_EQUAL, calls[name], yes="refuse")
    op(BPF_RETURN, RET_ALLOW)
    # an argument's low 32 bits alone: pid_t and the commands are 32 bits
    # wide, and the kernel ignores the rest of the register
    for name, allowed in guarded.items():
        labels[name] = len(program)
        op(BPF_LOAD, ARGS_OFFSET)
        for value in allowed:
            op(BPF_EQUAL, value & 0xFFFFFFFF, yes="allow")
        op(BPF_RETURN, RET_REFUSE)
    for name, denied in commands.items():
        labels[name] = len(program)
        op(BPF_LOAD, ARGS_OFFSET + 8)
        for value in denied:
            op(BPF_EQUAL, value, yes="refuse")
        op(BPF_RETURN, RET_ALLOW)
    # a space in each label here, so no call's name collides with one
    ends = (("allow", RET_ALLOW), ("refuse", RET_REFUSE), ("kill process", RET_KILL))
    for label, verdict in ends:
        labels[label] = len(program)
        op(BPF_RETURN, verdict)

    def jump(label: str | None, at: int) -> int:
        return 0 if label is None else labels[label] - at - 1

    return [(code, jump(yes, at), jump(no, at), k) for at, (code, k, yes, no) in enumerate(program)]


def _line(fd: int, deadline: float) -> bytes | None:
    """The child's result line, empty where the pipe closed without one, or
    `None` where the deadline passed first."""
    # up to the newline rather than to the pipe's close: a process the solution
    # forked holds the pipe open past the child's own exit
    chunks: list[bytes] = []
    while (left := deadline - time.monotonic()) > 0:
        ready, _, _ = select.select([fd], [], [], left)
        if not ready:
            break
        chunk = os.read(fd, 1 << 16)
        chunks.append(chunk)
        if not chunk or chunk.endswith(b"\n"):
            return b"".join(chunks)
    return None


if __name__ == "__main__":
    main()
