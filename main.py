import BusterScouting

TBAAUTHKEY = open("baller.txt").readline().removesuffix("\n")

scouter = BusterScouting.ScoutingHelper(TBAAUTHKEY)

print(scouter.getTeamEPAsAtEvent("2026ohmv"))