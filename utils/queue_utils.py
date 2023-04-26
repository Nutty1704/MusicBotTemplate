import random
from config import PREVIOUS_TRACKS, LOOPQ
import wavelink


def add_to_previous_queue(track: wavelink.Track):
    PREVIOUS_TRACKS.append(track)
    if len(PREVIOUS_TRACKS) > 10:
        PREVIOUS_TRACKS.pop(0)


def get_from_previous_tracks(pos: int) -> wavelink.Track:
    try:
        return PREVIOUS_TRACKS.pop(pos)
    except IndexError:
        return None


async def shuffle(queue: wavelink.WaitQueue):
    temp = []

    while not queue.is_empty:
        temp.append(queue.pop())

    random.shuffle(temp)

    while temp:
        await queue.put_wait(temp.pop())