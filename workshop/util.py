from prettytable import PrettyTable


def print_table(my_dict: dict, title: str = "Table"):
    # Create a table object
    table = PrettyTable()
    table.field_names = ["Score", "Times", "Probability"]

    # Add rows to the table
    for key, value in my_dict.items():
        table.add_row([key, value['sim'], value['prob']])

    # sorting table by Time column in descending order
    table.sortby = "Times"
    table.reversesort = True

    # Set the title of the table
    table.title = title

    # Print the table
    print(table)