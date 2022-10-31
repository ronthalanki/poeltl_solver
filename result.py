from enum import Enum

class ClosenessResult(Enum):
    GRAY = 0
    YELLOW = 1
    GREEN = 2

class UpDownResult(Enum):
    DOWN = 0
    UP = 1
    NEITHER = 2

@dataclass
class Result():
    player: ClosenessResult 
    conference: ClosenessResult 
    division: ClosenessResult
    team: ClosenessResult
    position: ClosenessResult
    age: Tuple[ClosenessResult, UpDownResult]
    no: Tuple[ClosenessResult, UpDownResult]
    height: Tuple[ClosenessResult, UpDownResult]