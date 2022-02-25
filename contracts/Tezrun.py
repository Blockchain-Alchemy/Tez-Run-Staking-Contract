import smartpy as sp

class Tezrun(sp.Contract):
    def __init__(self, owner):
        self.name = "Tezrun"
        self.init(
            owner = owner,
            raceId = 0,
            raceState = False,
            bets = sp.big_map(tvalue = 
                sp.TRecord(raceId = sp.TNat, horseId = sp.TNat, payout = sp.TNat, amount = sp.TMutez))
        )

    @sp.entry_point
    def startRace(self):
        sp.verify(self.is_owner(sp.sender))
        self.data.raceId += 1
        self.data.raceState = True

    @sp.entry_point
    def finishRace(self):
        sp.verify(self.is_owner(sp.sender))
        self.data.raceState = False

    @sp.entry_point
    def placeBet(self, params):
        sp.set_type(params, sp.TRecord(raceId = sp.TNat, horseId = sp.TNat, payout = sp.TNat))      

        sp.verify(sp.amount > sp.tez(0), "Invalid amount")
        sp.send(self.data.owner, sp.amount)

        self.data.bets[sp.sender] = sp.record(
            raceId = params.raceId,
            horseId = params.horseId,
            payout = params.payout,
            amount = sp.amount)

    # this is not part of the standard but can be supported through inheritance.
    def is_paused(self):
        return sp.bool(False)

    # this is not part of the standard but can be supported through inheritance.
    def is_owner(self, sender):
        return sender == self.data.owner
      

if "templates" not in __name__:
    @sp.add_test(name = "FA12")
    def test():
        scenario = sp.test_scenario()
        scenario.h1("Tezrun")

        # sp.test_account generates ED25519 key-pairs deterministically:
        admin = sp.test_account("Administrator")
        alice = sp.test_account("Alice")
        bob   = sp.test_account("Robert")

        # Let's display the accounts:
        scenario.h1("Accounts")
        scenario.show([admin, alice, bob])

        scenario.h1("Contract")
        c1 = Tezrun(admin.address)
        scenario += c1

        scenario.h1("Entry points")
        c1.startRace().run(sender = admin)
        scenario.verify(c1.data.raceId == 1)
        scenario.verify(c1.data.raceState == True)

        c1.placeBet(raceId = 1, horseId = 2, payout = 3).run(sender = alice, amount = sp.tez(10))

        c1.finishRace().run(sender = admin)
        scenario.verify(c1.data.raceState == False)