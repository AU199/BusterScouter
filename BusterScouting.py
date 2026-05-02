import statbotics
import requests
import pandas as pd

DEFAULT_FIELDS = [
    "team",
    "name",
    "state",
    "rookie_year",
    "record.wins",
    "record.losses",
    "record.winrate",
    "epa.total_points.mean",
    "epa.total_points.sd",
    "epa.breakdown.auto_points",
    "epa.breakdown.teleop_points",
    "epa.breakdown.endgame_points",
    "epa.ranks.total.rank",
    "epa.ranks.total.percentile",
    "epa.ranks.state.rank",
    "epa.ranks.state.percentile",
]


def _flatten(d: dict, parent_key: str = "", sep: str = ".") -> dict:
    out = {}
    for k, v in d.items():
        key = f"{parent_key}{sep}{k}" if parent_key else k
        out.update(_flatten(v, key, sep) if isinstance(v, dict) else {key: v})
    return out


class ScoutingHelper:

    def __init__(self, TBAKey: str):
        self.stats = statbotics.Statbotics()
        self.BASEURLTBA = "https://www.thebluealliance.com/api/v3"
        self.BASEURLStatbotics = "https://api.statbotics.io/v3"
        self.header = {"X-TBA-Auth-Key": TBAKey}

    def checkResponses(self):
        subURL = self.BASEURLTBA + "/status"
        response = self.req(subURL, self.header).status_code

        if response != 200:
            Warning(
                f"Status Code {response} is not 200, check configs in order to debug issue"
            )
            return
        else:
            print(f"{response} all good")
            return

    def getTeamsAtEvent(self, eventCode: str) -> pd.Series:
        """Function provides all team numbers as strings in the format 'frc#teamnumber#' as a pandas dataframe

        Args:
            eventCode (str): The event code of the event you want to prompt ex.'2025cmptx'

        Returns:
            pd.Dataframe: returns a pandas dataframe of team number
        """
        subURL = self.BASEURLTBA + f"/event/{eventCode}/teams/keys"
        teamList = self.req(subURL, self.header).json()
        return pd.Series(teamList)


    def getTeamEPAsAtEvent(
        self, eventCode: str, fields: list[str] | None = None
    ) -> pd.DataFrame:
        """Returns EPA stats for all teams at an event as a DataFrame.

        Args:
            eventCode (str): TBA event code e.g. '2026ohmv'
            fields (list[str] | None): Dot-notation fields to include (e.g. 'epa.total_points.mean').
                Defaults to DEFAULT_FIELDS. Pass [] for all fields.

        Returns:
            pd.DataFrame: One row per team, indexed by team number.
        """
        year, fields = int(eventCode[:4]), DEFAULT_FIELDS if fields is None else fields
        all_stats = [
            self.req(
                self.BASEURLStatbotics
                + f"/team_year/{int(t.removeprefix('frc'))}/{year}",
                None,
            ).json()
            for t in self.getTeamsAtEvent(eventCode)
        ]
        flat = [_flatten(s) for s in all_stats]
        df = pd.DataFrame(
            [{f: r[f] for f in fields if f in r} for r in flat] if fields else flat
        )
        return df.set_index("team") if "team" in df.columns else df


    def req(self, url, headers) -> requests.Response:
        return requests.get(url, headers)


if __name__ == "__main__":
    TBAAUTHKEY = open("baller.txt").readline().removesuffix("\n").removeprefix("\n")

    scouter = ScoutingHelper(TBAAUTHKEY)

    print(scouter.getTeamEPAsAtEvent("2026ohmv"))
