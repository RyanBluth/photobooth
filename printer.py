import cups
import json


def print_printers():
    conn = cups.Connection()
    printers = conn.getPrinters()
    pretty_print_dict(printers)


def pretty_print_dict(print_dic):
    print(json.dumps(print_dic, sort_keys=True, indent=4))


class Printer:
    name: str

    def __init__(self, name):
        self.name = name

    def print_attributes(self):
        pretty_print_dict(cups.Connection().getPrinterAttributes(self.name))
