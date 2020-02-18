import cups
import json
from typing import Dict


def print_printers():
    conn = cups.Connection()
    printers = conn.getPrinters()
    pretty_print_dict(printers)


def pretty_print_dict(print_dic):
    print(json.dumps(print_dic, sort_keys=True, indent=4))


class Printer:
    name: str
    connection: cups.Connection

    def __init__(self, name):
        self.name = name
        self.connection = cups.Connection()

    def print_attributes(self):
        pretty_print_dict(self.get_printer_attributes())

    def get_printer_attributes(self) -> Dict:
        return self.connection.getPrinterAttributes(self.name)

    def get_printer_state(self) -> int:
        return int(self.get_printer_attributes()["printer-state"])

    def resume_printer(self):
        self.connection.acceptJobs(self.name)

    def print_file(self, file: str):
        self.connection.printFile(self.name, file, "document", {})

    def cancel_all_jobs(self):
        self.connection.cancelAllJobs(name=self.name)
