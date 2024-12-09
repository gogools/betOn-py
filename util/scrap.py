
def get_place_in_str2int(word: str) -> int | None:
    if word.endswith("rs"):
        return int(word[:-2])
    elif word.endswith("nd"):
        return int(word[:-2])
    elif word.endswith("rd"):
        return int(word[:-2])
    elif word.endswith("th"):
        return int(word[:-2])
    try:
        return int(word)  # Try converting the entire word to an integer
    except ValueError:
        return None  # Return None if conversion fails


def get_points(points_str: str) -> dict:
    return {"points": points_str[:points_str.find(" ")],
            "pts_x_game": points_str[points_str.find("(") + 1:points_str.find(" per")]}


def get_record(record_str: str) -> dict:
    r_dict = record_str.split("-")
    return {"w": r_dict[0],
            "d": r_dict[1],
            "l": r_dict[2]}


def get_just_numbers(the_str: str) -> list:
    numbers = []
    number = ""

    for char in the_str:
        if char.isdigit():
            got_number = True
            number += char
        elif char == ".":  # Include decimal points
            got_point = True
            number += char
        else:
            if is_integer(number):
                numbers.append(int(number))
                number = ""
            elif is_float(number):
                numbers.append(float(number))
                number = ""
    if is_integer(number):
        numbers.append(int(number))
    elif is_float(number):
        numbers.append(float(number))

    return numbers


def is_integer(string):
    return string.isdigit()  # True for integers without signs


def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


def get_value_from_key(whole_str: str, key: str) -> str:
    return whole_str[len(key):].strip()