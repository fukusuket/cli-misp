from dataclasses import dataclass
import inquirer
from tabulate import tabulate
from pymisp import MISPEvent, MISPObject, PyMISP
import sys
import urllib3
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)

MISP_URL = "https://localhost/"
MISP_API_KEY = "9xlgP0x2tNi2cmpwAAnqZ0YzPuGcWVIbTGnoKuOT"


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
    attributes: list[(str, str, str)]

    def __str__(self):
        table = [
            ["ext_uuid", self.event_uuid],
            ["ticket_url", self.ticket_url],
            ["event_info", self.event_info],
        ]
        for key, val, _ in self.objects:
            table.append([key, val])
        for f in self.file_objects:
            table.append(["file", f"{f.name}, {f.cmdline} ..."])
        for key, val in self.attributes:
            table.append([key, val])
        return tabulate(table)


def build_misp_objects(ui: UserInput) -> list[MISPObject]:
    objects = []
    for type, val, comment in ui.objects:
        name = "url" if type == "url" else "domain-ip"
        obj = MISPObject(name=name)
        obj.add_attribute(type, value=val)
        if comment:
            obj.add_attribute("text", comment)
        objects.append(obj)
    for fo in ui.file_objects:
        obj = MISPObject(name='file')
        if fo.name:
            obj.add_attribute("filename", fo.name)
            obj.add_attribute("path", fo.name)
        if fo.sha256:
            obj.add_attribute('sha256', fo.sha256)
        if fo.cmdline:
            obj.add_attribute('text', fo.cmdline)
        if fo.date:
            obj.add_attribute('creation-time', fo.date)
        if fo.size:
            obj.add_attribute('size-in-bytes', int(fo.size))
        objects.append(obj)
    return objects


def build_misp_event(ui: UserInput, misp: PyMISP) -> (MISPEvent, bool):
    is_new_event = True
    event = MISPEvent()
    if ui.event_uuid:
        existing_event = misp.get_event(ui.event_uuid, pythonify=False)
        if "2" == str(existing_event["Event"]["orgc_id"]):
            event = existing_event
            event.delete_tag('workflow:state="complete"')
            event.add_tag('workflow:state="draft"')
            is_new_event = False
        else:
            event.extends_uuid = ui.event_uuid
    if is_new_event:
        event.info = ui.event_info
        event.distribution = 3
        event.analysis = 2
        event.threat_level_id = 1
        event.add_tag('tlp:green')
        event.add_tag('workflow:state="draft"')
        event.add_tag('course-of-action:active="deny"')
        event.add_tag('course-of-action:active="detect"')
        event.add_tag('estimative-language:confidence-in-analytic-judgment="high"')
        event.add_tag('estimative-language:likelihood-probability="very-likely"')
        event.add_tag('malware_classification:malware-category="Trojan"')
        event.add_attribute(type="comment", value=ui.ticket_url, comment="internal ticket url")
    for obj in build_misp_objects(ui):
        event.add_object(obj)
    for type, val, comment in ui.attributes:
        event.add_attribute(type=type, value=val ,comment=comment)
    if is_new_event:
        return event, True
    return event, False


def get_user_input() -> UserInput:
    ticket_url = input("(*) Redmine ticket URL: ")
    event_uuid = input("    UUID of an existing Event: ")
    event_info = input("(*) Event info: ")
    objects = []
    attributes = []
    file_objects = []
    questions = [
        inquirer.List(
            "ioc_type",
            message="(*) Choose IoC type: ",
            choices=["file", "url", "domain", "ip-src", "ip-dst", "log", "other"],
        ),
    ]
    while True:
        ans = inquirer.prompt(questions)
        ioc_type = ans["ioc_type"]
        if ioc_type == "file":
            v1 = input(f"(*) file name or path: ").strip()
            v2 = input(f"    file command line: ").strip()
            v3 = input(f"    file size in bytes(int): ").strip()
            v4 = input(f"    file creation date(e.g. 2024-01-01T23:59:59): ").strip()
            v5 = input(f"    file sha256: ").strip()
            file_objects.append(MyFileObject(v1, v2, v3, v4, v5))
        else:
            ioc_value = input(f"(*) IoC value[{ioc_type}]: ").strip()
            if ioc_value:
                ioc_comment = input(f"    log or comment for[{ioc_value}]: ").strip()
                ioc_comment = "" if not ioc_comment else ioc_comment
                if ioc_type == "other":
                    attributes.append((ioc_type, ioc_value, ioc_comment))
                else:
                    objects.append((ioc_type, ioc_value, ioc_comment))
        ans = input("Do you have another IoC? [y/n]: ")
        if not ans or ans[0].lower() == "n":
            ui = UserInput(event_uuid, ticket_url, event_info, objects, file_objects, attributes)
            print("Event preview:")
            print(ui)
            ans = input("Add above event to MISP? [y/n]: ")
            if not ans or (ans and ans[0].lower() == "y"):
                return ui
            else:
                continue


def check_misp_connection(url, key) -> PyMISP:
    try:
        return PyMISP(url, key, False)
    except Exception as e:
        print("Failed to connect MISP. Please check MISP_URL/MISP_API_KEY.")
        sys.exit()


if __name__ == "__main__":
    misp = check_misp_connection(MISP_URL, MISP_API_KEY)
    user_input = get_user_input()
    misp_event, is_new_event = build_misp_event(user_input, misp)
    print("")
    if is_new_event:
        print("Start to adding event to misp.")
        res = misp.add_event(misp_event)
    else:
        print("Start to updating event to misp.")
        res = misp.update_event(misp_event)
    print("Adding event done successfully!")
    print("")
    print(f"You can view added event:")
    print(f"{MISP_URL}/events/view/{str(res['Event']['id'])}")
    print(f"{str(res['Event']['uuid'])}")
    print("")
