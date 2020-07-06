import os
import json

def remove_empty_abstract_files(path):
    if os.path.isdir(path) == False:
        print("Entered path is wrong!")
        return

    removed_item = 0
    for root, dirs, files in os.walk(path):
        for name in files:
            filename = os.path.join(root, name)
            with open(filename) as json_file:
                data = json.load(json_file)
            if not data["abstract"]:
                print(" Removing ", filename)
                try:
                    os.remove(filename)
                    removed_item += 1
                except:
                    print("Error while removing ", filename)

    print(f"Removed totally {removed_item} files")
remove_empty_abstract_files("../microorganisms")

