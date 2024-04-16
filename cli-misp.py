from simple_term_menu import TerminalMenu
from rich import print


def main():
    event_info = input("Enter Event info: ")
    op1 = ["ip-dst", "ip-src", "domain", "url", "filename", "filepath", "md5", "sha256", "registry"]
    ioc_types = TerminalMenu(op1)
    attributes = []
    while True:
        print("Choose IoC type: ")
        ioc_type = ioc_types.show()
        ioc_value = input(f"Enter IoC value[{op1[ioc_type]}]: ")
        attributes.append((ioc_type, ioc_value))
        user_input = input("Do you have another IoC?[y/n]: ")
        if user_input.lower() == "n":
            break

    op2 = ["beg", "baf", "fw"]
    attacked_area = TerminalMenu(op2)
    print("Choose Attacked area: ")
    ioc_area = attacked_area.show()
    print(op2[ioc_area])

    op3 = ["deny", "disrupt", "detection"]
    action = TerminalMenu(op3)
    print("Choose Course of action: ")
    ioc_action = action.show()
    print(op3[ioc_action])

    while True:
        input("Enter MITRE ATT&CK TID: ")
        user_input = input("Do you have another TIDs?[y/n]: ")
        if user_input.lower() == "n":
            break
    url = input("Enter Redmine ticket URL: ")

if __name__ == "__main__":
    main()