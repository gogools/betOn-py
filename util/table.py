import operator
import re

from bs4 import Tag
from prettytable import PrettyTable

# mine
import util
from util import msg

CELL_404 = "cell_404"

def print_table(data: list, title: str = "Table", sort_by_columns: list = None, reverse: bool = False):
    util.msg(f"about to print table: {title}")

    if data is None or len(data) == 0 or all(isinstance(d, dict) and len(d) == 0 for d in data):
        util.err(f"Table data must be a non-empty list or a list of empty dictionaries. Title: {title}")
        return

    table = PrettyTable()

    table.title = title
    data = sort_table(data, sort_by_columns, reverse)

    first_row = True
    for d in data:
        if first_row:
            table.field_names = d.keys()
            first_row = False
        table.add_row(d.values() if isinstance(d, dict) else d)

    print(table)


def sort_table(table: list, sort_by_columns: list = None, reverse: bool = False) -> list:
    if is_2d_list(table) and sort_by_columns is not None and len(sort_by_columns) > 0:
        ordering_key = operator.itemgetter(*sort_by_columns)
        table.sort(key=ordering_key, reverse=reverse)
    return table


def is_2d_list(list_to_check) -> bool:  # Check if a list is a 2d list or a table
    if not isinstance(list_to_check, list):
        return False  # Not a list at all
    return all(isinstance(row, list) or isinstance(row, dict) for row in list_to_check)  # True if all rows are lists or dicts


def sort_and_get_row(table: list, sort_by_columns: list = None, reverse: bool = False, row: int = 0) -> list:
    table = sort_table(table, sort_by_columns, reverse)  # already validates if table is a 2d list
    return table[row]


def get_table_headers(table: Tag) -> list:
    headers = []
    first_headers = True
    for tr in table.find("thead").find_all("tr"):

        #continue if style="display: none;"
        if tr.get("style") is not None and "display: none;" in tr.get("style"):
            continue

        aux_headers = []
        h_repeat = 0

        for th in tr.find_all("th"):
            h = th.text.strip().lower().replace(" ", "_")
            h_repeat = h_repeat+1 if h in aux_headers else h_repeat
            aux_headers = aux_headers + [f"{h}{h_repeat}" if h in aux_headers and len(h) != 0 else h ] * (int(th["colspan"]) if "colspan" in th.attrs else 1)

        headers = [""] * len(aux_headers) if first_headers else headers
        headers = [x + ('' if first_headers else '_') + y for x, y in zip(headers, aux_headers)]
        first_headers = False

    return [(h[1:] if h.find('_') == 0 else h) for h in headers]


def get_table_data(table: Tag, base_url: str = None) -> list:

    result = []

    headers = get_table_headers(table)

    if base_url is None:
        base_url = ""
    elif re.match(util.REGEX_URL_PATTERN, base_url):
        base_url = base_url.split("/")[0] + "//" + base_url.split("/")[2]
    else:
        base_url = ""

    for row in table.find("tbody").find_all("tr"):

        if row.get("class") is not None and "thead" in row.get("class"):
            continue

        whole_row = row.find_all("th") + row.find_all("td")

        if len(whole_row) != len(headers):
            continue

        row_dict = {}
        for i, cell in enumerate(headers):
            if whole_row[i].find("a") is not None:
                row_dict[cell] = util.val(whole_row[i].text)
                row_dict[cell+'_url'] = f"{base_url}{whole_row[i].find("a").get("href")}"
            elif whole_row[i].find("ul") is not None:
                li_list = whole_row[i].find("ul").findAll("li")
                row_dict[cell] = ", ".join([li.text.strip() if li.text.strip() else "-".join(li['class']) for li in li_list])
            else:
                row_dict[cell] = util.val(whole_row[i].text)

        result.append(row_dict)

    return result


def get_table_footers(table: Tag, headers: list) -> list:
    footers = []
    tfoot = table.find("tfoot")

    if tfoot is None:
        return footers

    for row in tfoot.find_all("tr"):
        whole_row = row.find_all("th") + row.find_all("td")
        if len(headers) == len(whole_row):
            footers.append({headers[i]: util.val(col.text) for i, col in enumerate(whole_row)})

    return footers

def get_whole_table(table: Tag, base_url: str) -> dict:
    print(f"get_whole_table of table_id:{table.get('id') if table is not None else "Table 404"}")

    if table is None:
        return {}

    stats = []
    headers = get_table_headers(table)
    for row in get_table_data(table, base_url):
        data_dict = {}
        empty_headers = 0
        for h in headers:
            if len(h) == 0:
                empty_headers += 1
                data_dict[f"h{empty_headers}"] = util.val(row[h])
            else:
                data_dict[h] = util.val(row[h])
        # data_dict = {h : util.val(row[h]) for h in headers}
        if all(value == "" for value in data_dict.values()):
            continue
        stats.append(data_dict)

    result = {
        "data": stats
    }

    footers = get_table_footers(table, get_table_headers(table))
    if len(footers) > 0:
        result["total"]= footers

    return result


def show_table(mined_stuff: dict, main_title: str = ""):

    if isinstance(mined_stuff, dict) and len(mined_stuff) > 0:
        keys = list(mined_stuff.keys())

        title_appendix = f"{main_title}"
        for key in keys:
            data = mined_stuff[key]
            title = key.replace("_", " ").title() + title_appendix

            if not isinstance(data, dict) and not isinstance(data, list):
                title_appendix += f" {data}" #TODO check if this is necessary
                continue

            if len(data) > 0 and isinstance(data, list) and all(isinstance(x, dict) for x in data):
                print_table(data, title)
            elif len(data) > 0 and isinstance(data, dict) and "data" in data and "total" in data:
                print_table(data["data"], title)
                print_table([] if len(data["total"]) == 0 else data["total"], f"Totals - {title}")
            elif len(data) > 0 and isinstance(data, dict) and all(isinstance(x, (str, int, float)) for x in data.values()):
                print_table([data], title)
            elif len(data) > 0 and isinstance(data, dict):
                show_table(data, f" {title}")
            elif len(data) > 0 and isinstance(data, list) and all(isinstance(x, str) for x in data):
                print_table([{'data': item} for item in data], title)
            elif len(data) > 0 and isinstance(data, list):
                for d in data:
                    if isinstance(d, dict):
                        show_table(d, f" {title}")
                    elif isinstance(d, list) and all(isinstance(x, str) for x in d):
                        print_table([{'data': item} for item in data], title)

    else:
        msg("No data to show")