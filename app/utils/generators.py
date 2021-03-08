import itertools
from typing import Generator, Sequence, Tuple, TypeVar


T = TypeVar("T")


def grouper(
    iterable: Sequence[T], size: int
) -> Generator[Tuple[T], None, None]:
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, size))
        if not chunk:
            return
        yield chunk
