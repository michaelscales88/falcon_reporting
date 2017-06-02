from sqlalchemy import Integer, DateTime, String
import numpy as np
from numpy import object_, int64
from sqlalchemy_utils import Timestamp       # sqlalchemy provided mixins


COLUMNS = {
    np.object_: String,
    int64: Integer,
    np.datetime64: DateTime
}


class TimeStamp(Timestamp):                  # Change name for import
    pass



