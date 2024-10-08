import os
import sys
from threading import Lock, Thread
from typing import Callable, Optional, Union

try:
    import tqdm
    PROGRESS = bool(os.environ.get("PYSLOTH_PROGRESSBAR", True))
except ImportError:
    print("Install tqdm to enable progressbar", file=sys.stderr)
    PROGRESS = False

from _sloth import ffi, lib

progressbar = None

if PROGRESS:

    @ffi.def_extern()
    def update_progress(delta_iterations):
        if progressbar is not None:
            progressbar.update(delta_iterations)

else:

    @ffi.def_extern()
    def update_progress(delta_iterations):
        pass


class Sloth:
    """
    Object wrapper for the sloth c library.

    :param data: String or bytes of input data
        will be converted to bytes if sting
    :param bits: Number of bits to use for prime numbers in sloth
        Must be a multiple of 512
    :param iterations: Number of square root permutations in sloth
        Most significant parameter in delay function
    :param final_hash: Sloth output hash as bytes
        Can be used for verification
    :param witness: Sloth output witness as bytes
        Can be used for verification
    :param blocking: Block if True else run tasks in thread
    """

    def __init__(
        self,
        data: Optional[Union[bytes, str]] = None,
        bits: int = 2048,
        iterations: int = 50000,
        final_hash: Optional[bytes] = None,
        witness: Optional[bytes] = None,
        blocking: bool = False,
    ):
        assert isinstance(bits, int)
        assert (bits % 512) == 0
        assert isinstance(iterations, int)
        self._data = None
        if data is not None:
            self.data = data
        self.bits = bits
        self.iterations = iterations
        self.final_hash = final_hash
        self.witness = witness
        self.valid = None
        self.blocking = blocking
        self._thread = None
        self._lock = Lock()

    @property
    def data(self) -> Optional[bytes]:
        return self._data

    @data.setter
    def data(self, value):
        if isinstance(value, bytes):
            self._data = value
            return
        elif not isinstance(value, str):
            value = str(value)
        self._data = value.encode("utf8")

    def compute(self):
        def compute_task():
            out = ffi.new("unsigned char[64]")
            witness = ffi.new("unsigned char[{}]".format(int(self.bits / 8)))
            witness_size = ffi.new("size_t*")
            lib.sloth(witness, witness_size, out, self.data, self.bits, self.iterations)
            witness_size = witness_size[0]
            with self._lock:
                self.witness = bytes(ffi.buffer(witness, witness_size))
                self.final_hash = bytes(ffi.buffer(out))

        self._run(task=compute_task)

    def verify(self):
        def verify_task():
            assert self.witness is not None
            verification = lib.sloth_verification(
                self.witness,
                len(self.witness),
                self.final_hash,
                self.data,
                self.bits,
                self.iterations,
            )
            with self._lock:
                self.valid = verification == 1

        self._run(task=verify_task)

    def _run(self, task: Callable):
        global progressbar
        if not self.blocking:
            self.wait()
        if PROGRESS:
            progressbar = tqdm.tqdm(total=self.iterations)

        def wrapped_task():
            task()
            if PROGRESS:
                progressbar.close()

        if self.blocking:
            wrapped_task()
        else:
            self._thread = Thread(target=wrapped_task, daemon=True)
            self._thread.start()

    def wait(self, timeout: Optional[int] = None):
        if self._thread is not None:
            self._thread.join(timeout=timeout)



def sloth(data, iterations):
    s = Sloth(data, iterations=iterations, blocking=True,bits=1024)
    s.compute()
    return [s.witness.hex(), s.final_hash.hex(), s.data.hex()]
def verify_sloth(witness,final_hash,data_to_match,iterations):
    s = Sloth(iterations=iterations, final_hash=final_hash, witness=witness, blocking=True,bits=1024,data=data_to_match)
    s.verify()
    return s.valid

def hello():
    print("Hello from sloth.py")


if __name__ == "__main__":
    import json
    action = sys.argv[1]  # Either 'compute' or 'verify'
    if action == 'sloth':
        data = sys.argv[2]
        iterations = int(sys.argv[3])
        result = sloth(data, iterations)
        print(result)
    elif action == 'verify':
        data = bytes.fromhex(sys.argv[2])
        final_hash = bytes.fromhex(sys.argv[3])
        witness = bytes.fromhex(sys.argv[4])
        iterations = int(sys.argv[5])
        valid = verify_sloth(witness, final_hash, data, iterations)
        print(valid)

# if __name__ == "__main__":
#     sloth_art = """
#       `""==,,__
#         `"==..__"=..__ _    _..-==""_
#              .-,`"=/ /\ \""/_)==""``
#             ( (    | | | \/ |
#              \ '.  |  \;  \ /
#               |  \ |   |   ||
#          ,-._.'  |_|   |   ||
#         .\_/\     -'   ;   Y
#        |  `  |        /    |-.
#        '. __/_    _.-'     /'
#               `'-.._____.-'
# """
#     print(sloth_art)
#     if len(sys.argv) > 1:
#         sloth_art = sys.argv[1].encode("utf-8")
#         print("input is", sloth_art)
#     import time
#     from datetime import timedelta

#     s = Sloth(sloth_art, bits=1024, iterations=100, blocking=True)
#     print("Bits: {}\tIterations: {}".format(s.bits, s.iterations))
#     t = time.time()
#     print("{:=^50}".format(" COMPUTE "))
#     s.compute()
#     print("Witness:", s.witness)
#     print("Output data:", s.final_hash)
#     print("Time:", timedelta(seconds=time.time() - t))
#     print("{:=^50}".format(" VERIFY "))
#     t = time.time()
#     s.verify()
#     print("Verify:", "VALID" if s.valid else "INVALID", "sloth")
#     print("Time:", timedelta(seconds=time.time() - t))
#     items = sloth(sloth_art, 10)
#     print(verify_sloth(witness=items[0], final_hash=items[1], data_to_match=items[2] , iterations=10))

