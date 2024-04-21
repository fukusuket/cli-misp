from simple_term_menu import TerminalMenu
from rich import print


class UserInput:
    pass


def get_user_input():
    redmine_url = input("Enter Redmine ticket URL: ")
    event_info = input("Enter Event info[e.g. [where]_[what]_[how]]: ")
    ioc_type_opt = ["ip", "domain", "url", "filepath", "md5", "sha256", "other"]
    attributes = []
    while True:
        print("Choose IoC type: ")
        ioc_type = TerminalMenu(ioc_type_opt).show()
        ioc_value = input(f"Enter IoC value[{ioc_type_opt[ioc_type]}]: ")
        attributes.append((ioc_type, ioc_value))
        user_input = input("Do you have another IoC?[y/n]: ")
        if user_input.lower() == "n":
            break

    op3 = ["deny", "disrupt", "detection"]
    action = TerminalMenu(op3)
    print("Choose Course of action: ")
    ioc_action = action.show()
    print(op3[ioc_action])

    while True:
        tid = input("Enter MITRE ATT&CK TID: ")
        user_input = input("Do you have another TIDs?[y/n]: ")
        if user_input.lower() == "n":
            break


if __name__ == "__main__":
    get_user_input()