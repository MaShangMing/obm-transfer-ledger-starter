"""Small local stock-transfer baseline with snapshot persistence."""
import copy
from pathlib import Path
from journal import read_records, save

class Store:
    def __init__(self, directory, seed, hook=None):
        self.path = Path(directory) / "ledger.wal"
        self.hook = hook
        self.seed = copy.deepcopy(seed)
        self.bins = {key: dict(value, revision=0) for key, value in seed.items()}
        self.number = 0
        self.receipts = {}
        records = read_records(self.path)
        if records:
            for row in records[1:]:
                self.bins = row["bins"]
                self.number = row["receipt"]["number"]
                self.receipts[row["receipt"]["ticket"]] = row["receipt"]
        else:
            save(self.path, {"seed": seed}, self.hook)

    def apply(self, request):
        ticket = request["ticket"]
        if ticket in self.receipts:
            return self.receipts[ticket]
        touched = {leg[key] for leg in request["moves"] for key in ("from", "to")}
        before = {key: copy.deepcopy(self.bins[key]) for key in sorted(touched)}
        decision = "committed"
        for leg in request["moves"]:
            src, dst, units = leg["from"], leg["to"], leg["units"]
            if self.bins[src]["quantity"] < units:
                decision = "shortage"
                break
            self.bins[src]["quantity"] -= units
            self.bins[dst]["quantity"] += units
            self.bins[src]["revision"] += 1
            self.bins[dst]["revision"] += 1
        self.number += 1
        receipt = {"ticket": ticket, "decision": decision, "number": self.number,
                   "before": before, "after": {k: copy.deepcopy(self.bins[k]) for k in sorted(touched)}}
        if decision == "committed":
            save(self.path, {"receipt": receipt, "bins": self.bins}, self.hook)
            self.receipts[ticket] = receipt
        return receipt

    def snapshot(self):
        return {"number": self.number, "bins": self.bins}

    def close(self):
        pass
