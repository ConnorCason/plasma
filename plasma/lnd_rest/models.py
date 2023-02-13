

class Forward:
    def __init__(self, chanId, ts, amt_in, fee, amt_out):
        self.chanId = chanId
        self.ts = ts
        self.amt_in = amt_in
        self.fee = fee
        self.amt_out = amt_out