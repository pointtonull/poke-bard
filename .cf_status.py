import json
from pprint import pformat

from dateutil.parser import parse as parsetimestamp


SILENCE_STATUSES = [
    "CREATE_COMPLETE",
    "CREATE_IN_PROGRESS",
    "DELETE_COMPLETE",
    "DELETE_IN_PROGRESS",
    "REVIEW_IN_PROGRESS",
    "ROLLBACK_COMPLETE",
    "ROLLBACK_IN_PROGRESS",
    "UPDATE_COMPLETE",
    "UPDATE_COMPLETE_CLEANUP_IN_PROGRESS",
    "UPDATE_IN_PROGRESS",
    "UPDATE_ROLLBACK_COMPLETE",
    "UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS",
    "UPDATE_ROLLBACK_IN_PROGRESS",
]

BAD_REASONS = ("Resource update cancelled", "Resource creation cancelled")


def get_time(event):
    return parsetimestamp(event["Timestamp"])


def tprint(title):
    print("%s\n%s\n" % (title, "#" * len(title)))


def iformat(string, indent=0):
    if not isinstance(object, str):
        string = pformat(string)
    return ("\n" + " " * indent).join(string.splitlines())


def main():
    messages = json.load(open(".cf.messages"))
    events = messages["StackEvents"]

    relevant = []
    ignored = set()
    last_time = get_time(events[0])
    for event in events:
        age = last_time - get_time(event)
        status = event.get("ResourceStatus")
        if age.seconds > 60:
            break
        last_time = get_time(event)
        if status not in SILENCE_STATUSES:
            if event.get("ResourceStatusReason") in BAD_REASONS:
                break
            event["RelativeAge"] = str(age)
            relevant.append(event)
            continue
        ignored.add(status)
    if ignored:
        print("Ignoring %s" % ", ".join(ignored))

    if relevant:
        print("\nTraceback (most recent event at botom):")
        for event in relevant[::-1]:
            status = event.pop("ResourceStatus")
            properties = event.get("ResourceProperties", "{}")
            try:
                event["ResourceProperties"] = json.loads(properties)
            except Exception as e:
                print("could not process properties '{properties}' (failed with error %s" % error)
            print(status)
            for key, value in event.items():
                print("    %s: %s" % (key, iformat(value, 8)))
            print("")
    else:
        print("CloudFormation Stack's logs looks clear.")


if __name__ == "__main__":
    main()
