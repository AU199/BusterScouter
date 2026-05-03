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
        
        returnDataframe = self.getTeamsEpa(self.getTeamsAtEvent(eventCode).to_list(), year, fields)
        
        return returnDataframe  

    def getTeamEPA(
        self, teamCode:str|int, year: int, fields: list[str] | None = None
    ) -> pd.DataFrame:
        """provided a team number and year, this returns a pandas dataframe with all the requested fields

        Args:
            teamCode (str | int): team number, can be passed in as either "frc#teamnumber#" or the team code
            year (int): the year must be an integer 
            fields (list[str] | None): Dot-notation fields to include (e.g. 'epa.total_points.mean').
                Defaults to DEFAULT_FIELDS. Pass [] for all fields..

        Returns:
            pd.DataFrame: Dataframe containing all requested fields for the given team. The team in the column 
        """
        
        
        if (self.safetyCaptain(teamCode,[str,int])):
            
            print(type(teamCode))
            if isinstance(teamCode,str):
                if "frc" in teamCode:
                    teamNumber = int(teamCode.removeprefix("frc"))
                else:
                    teamNumber = int(teamCode)
            else: 
                teamNumber = teamCode
            allStats = [
                self.req(
                    self.BASEURLStatbotics
                    + f"/team_year/{int(teamNumber)}/{year}",
                    None,
                ).json()
            ]
            if len(allStats) < 1:
                Warning(f"The provided team number {teamNumber} is invalid or the team was not active in the given year, please double check the team that was being requested")

            flat = _flatten(allStats[0]) 
            cols = list(dict.fromkeys(["team"] + fields)) if fields else None
            teamData = pd.Series({f: flat[f] for f in cols if f in flat} if cols else flat)
            return teamData.rename(flat['team'])



    def getTeamsEpa(self, teams: list[str] | list[int], year: int, fields: list[str] | None = None) -> pd.DataFrame:
        teamsDfRows = []
        teams.sort()
        for team in teams:
            
            if self.safetyCaptain(team,[str,int]):
                
                individualTeamEPADF = self.getTeamEPA(team,year,fields)
                teamsDfRows.append(individualTeamEPADF)
            
            else:
                Warning(f"A wrong type was passed in for the team code, please double check" )
                return pd.DataFrame()
        return pd.DataFrame(teamsDfRows)
        
    
    
    def safetyCaptain(self,objToBeChecked:object, typeItShouldBe:list[type] | type) -> bool:
    
        if isinstance(objToBeChecked, tuple(typeItShouldBe)):
            return True
        else:
            return False
        
    
    
    
    def req(self, url, headers) -> requests.Response:
        return requests.get(url, headers)


if __name__ == "__main__":
    
    TBAAUTHKEY = open("baller.txt").readline().removesuffix("\n").removeprefix("\n")

    scouter = ScoutingHelper(TBAAUTHKEY)

    print(scouter.getTeamEPAsAtEvent("2026ohmv"))
