from db import get_conn

class Location:
    def __init__(self, BRANCH_ID, NAME, ADDRESS, LAT, LNG, OPEN_HOURS, CREATED_AT):
        self.BRANCH_ID = BRANCH_ID
        self.NAME = NAME
        self.ADDRESS = ADDRESS
        self.LAT = LAT
        self.LNG = LNG
        self.OPEN_HOURS = OPEN_HOURS
        self.CREATED_AT = CREATED_AT
