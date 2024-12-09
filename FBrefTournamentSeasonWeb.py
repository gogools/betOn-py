from fastapi import FastAPI, Request

from crawler_scrapper import FBrefLeaguesStatsScrapper

app = FastAPI(synchronous=True)


@app.get("/fbref/tournament/{tournament}/season/{season}")
async def fbref_tournament_season(request: Request, tournament: str, season: str):
    print(f"fbref tournament API: {tournament} season: {season}")

    scrapper = FBrefLeaguesStatsScrapper(tournament, season)
    return scrapper.scrap()
