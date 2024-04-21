from dataclasses import dataclass
from simple_term_menu import TerminalMenu
from tabulate import tabulate
from pymisp import MISPEvent, MISPObject, PyMISP
import urllib3
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)

MISP_URL = "https://localhost"
MISP_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxx"


@dataclass(frozen=True)
class MyFileObject:
    name: str
    cmdline: str
    size: str
    date: str
    sha256: str


@dataclass(frozen=True)
class UserInput:
    event_uuid: str
    ticket_url: str
    event_info: str
    objects: list[(str, str, str)]
    file_objects: list[MyFileObject]
    attributes: list[(str, str)]

    def __str__(self):
        table = [
            ["extended_uuid", self.event_uuid],
            ["ticket_url", self.ticket_url],
            ["event_info", self.event_info],
        ]
        for key, val, _ in self.objects:
            table.append([key, val])
        for f in self.file_objects:
            table.append(["file", f"{f.name}, {f.cmdline},f{f.date}, f{f.size}, {f.sha256}" ])
        for key, val in self.attributes:
            table.append([key, val])
        return tabulate(table)


def build_misp_objects(ui: UserInput) -> list[MISPObject]:
    objects = []
    for type, val, comment in ui.objects:
        name = "url" if type == "url" else "domain-ip"
        obj = MISPObject(name=name)
        obj.add_attribute(type, value=val)
        objects.append(obj)
    for fo in ui.file_objects:
        obj = MISPObject(name='file')
        obj.add_attribute("filename", fo.name)
        obj.add_attribute("path", fo.name)
        obj.add_attribute('sha256', fo.sha256)
        obj.add_attribute('text', fo.cmdline)
        obj.add_attribute('creation-time', fo.date)
        obj.add_attribute('size-in-bytes', int(fo.size))
        objects.append(obj)
    return objects


def build_misp_event(ui: UserInput) -> MISPEvent:
    event = MISPEvent()
    if ui.event_uuid:
        event.extends_uuid = ui.event_uuid
    event.info = ui.event_info
    event.distribution = 3
    event.analysis = 2
    event.threat_level_id = 1
    event.add_tag('tlp:amber+strict')
    event.add_tag('workflow:state="draft"')
    event.add_tag('course-of-action:active="deny"')
    event.add_tag('course-of-action:active="detect"')
    event.add_tag('estimative-language:confidence-in-analytic-judgment="high"')
    event.add_tag('estimative-language:likelihood-probability="very-likely"')
    for obj in build_misp_objects(ui):
        event.add_object(obj)
    for type, val in ui.attributes:
        event.add_attribute(type, val)
    event.add_attribute(type="comment", value=ui.ticket_url, comment="internal ticket url")
    return event


def get_user_input() -> UserInput:
    event_uuid = input("UUID of an existing Event(If not exist, leave it blank): ")
    ticket_url = input("Redmine ticket URL: ")
    event_info = input("Event info(e.g. where_what_how): ")
    objects = []
    attributes = []
    file_objects = []
    ioc_type_opt = ["file", "url", "domain", "ip-src", "ip-dst", "other"]
    while True:
        print("Choose IoC type(blank if there is no input value): ")
        ioc_type_index = TerminalMenu(ioc_type_opt).show()
        ioc_type = ioc_type_opt[ioc_type_index]
        if ioc_type == "file":
            v1 = input(f"file name or path(e.g. /tmp/XAv1s): ").strip()
            v2 = input(f"file command line(e.g. /tmp/XAv1s -h bad.example.com): ").strip()
            v3 = input(f"file size in bytes(e.g. 256): ").strip()
            v4 = input(f"file creation date(e.g. 2024-01-01T00:00:00): ").strip()
            v5 = input(f"file sha256: ").strip()
            file_objects.append(MyFileObject(v1, v2, v3, v4, v5))
        elif ioc_type == "other":
            ioc_value = input(f"IoC value[{ioc_type}]: ").strip()
            attributes.append((ioc_type, ioc_value))
        else:
            ioc_value = input(f"IoC value[{ioc_type}]: ").strip()
            ioc_comment = input(f"log or comment(If not comment, leave it blank): ").strip()
            objects.append((ioc_type, ioc_value.strip(), ioc_comment.strip()))
        if input("Do you have another IoC?[y/n]: ").lower() == "n":
            ui = UserInput(event_uuid, ticket_url, event_info, objects, file_objects, attributes)
            print("")
            print("Event preview:")
            print(ui)
            if input("Add above event to MISP?[y/n]:").lower() == "y":
                return ui
            else:
                continue


if __name__ == "__main__":
    user_input = get_user_input()
    misp_event = build_misp_event(user_input)
    print("")
    print(f"Start to connect MISP[{MISP_URL}].")
    misp = PyMISP(MISP_URL, MISP_API_KEY, False)
    print(f"Connecting to MISP[{MISP_URL}] done.")
    print("")
    print("Start to adding event to misp.")
    res = misp.add_event(misp_event)
    print("Adding event done successfully!")
