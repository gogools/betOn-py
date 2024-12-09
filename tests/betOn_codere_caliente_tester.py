from googletrans import Translator  # pip install googletrans==3.1.0a0

# my python files to tests
from candidates2delete.web_crawler_leagues_codere_caliente import get_codere_caliente_tournament_url as get_CC_tourney_url

tournament = "PremierLeague"
country = "England"


def test_get_codere_tourney_url():
    global tournament, country

    print(f"\nTesting get_codere_caliente_tournament_url(), Input to test: {tournament}, {country}")

    translator = Translator()
    country_es = translator.translate(country, src="en", dest='es').text

    tournament_url = get_CC_tourney_url("https://apuestas.codere.mx", "/es_MX/futbol", tournament, country_es)
    print(f"Tournament url: {tournament_url}")


def test_get_caliente_tourney_url():
    global tournament, country

    print(f"\nTesting get_codere_caliente_tournament_url(), Input to test: {tournament}, {country}")

    translator = Translator()
    country_es = translator.translate(country, src="en", dest='es').text

    tournament_url = get_CC_tourney_url("https://sports.caliente.mx", "/es_MX/Futbol", tournament, country_es)
    print(f"Tournament url: {tournament_url}")


if __name__ == "__main__":
    test_get_codere_tourney_url()
    test_get_caliente_tourney_url()
