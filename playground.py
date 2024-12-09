# fuzzywuzzy
from fuzzywuzzy import fuzz  # needs pip install python-Levenshtein

country = "England"

print(f"ratio:{fuzz.partial_ratio(country, "Albania Football Clubs")}, <a>: {"Albania Football Clubs"}")
print(f"ratio:{fuzz.partial_ratio(country, "England Football Clubs")}, <a>: {"England Football Clubs"}")
print(f"ratio:{fuzz.partial_ratio(country, "Mexico Football Clubs")}, <a>: {"Mexico Football Clubs"}")

print(f"ratio:{fuzz.ratio("Premier League", "Premier League")}, <a>: {"Premier League"}")
print(f"ratio:{fuzz.ratio("PremierLeague", "Premier League")}, <a>: {"Premier League"}")
print(f"ratio:{fuzz.partial_ratio("Premier League", "Premier League")}, <a>: {"Premier League"}")
print(f"ratio:{fuzz.partial_ratio("PremierLeague", "Premier League")}, <a>: {"Premier League"}")

original_string = "This is a tests string."
substring = "tests"
new_string = original_string.replace(substring, "replaced")

print(f"Original string: {original_string}")
print(f"New string: {new_string}")

name = "Andr\u00e9 Onana"
print(name)