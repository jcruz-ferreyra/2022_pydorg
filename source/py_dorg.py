### Downloads Organizer ###

# Script to detect and remove duplicates in 'downloads' folder
# Then organize each files with the same extension in specific folder

import datetime
import os
import re
import shutil
from pathlib import Path
from pprint import pprint

import pyinputplus as pyip
from send2trash import send2trash

os.chdir(Path.home() / "Downloads")


# ---------- Functions ----------


def DupChecker(currentFile, dupList, delList):
    """
    Function that creates a list for duplicated files to be deleted

    First checks by the name of the file if it may be a duplicated one,
    If it founds it, checks for another file that may be the original one,
    If it found it, compare sizes of both files.
    :input: each single filename in Downloads folder,
    :input: list for 'seems like duplicated file' but with no original file found,
    :input: list for 'seems like duplicated file' and original file found.
    :output: none or the correponding list with the current filename.
    """
    # Check if file seems like a duplicated file with regex
    dupRegex = re.compile(
        r"""(
                                ((\s+)?-(\s+)?copia)?((\s+)?-(\s+)?copy)?(\s+)?\(\d+\).\w+|
                                ((\s+)?\(\d+\))?(\s+)?-(\s+)?copia.\w+|
                                ((\s+)?\(\d+\))?(\s+)?-(\s+)?copy.\w+
                                )""",
        re.VERBOSE,
    )
    moDup = dupRegex.search(currentFile)

    if moDup:
        # Check if there is another file that matches 'probably duplicated' filename
        suffix = moDup.group()
        origFilename = currentFile.replace(suffix, "")

        for newFile in os.listdir("."):
            if newFile != currentFile:
                origRegex = re.compile(rf"""{origFilename}""")
                moOrig = origRegex.search(newFile)

                if moOrig:
                    if os.path.getsize(newFile) == os.path.getsize(currentFile):
                        delList.append(currentFile)
                        return delList
                    else:
                        continue
                else:
                    continue

            else:
                continue
        dupList.append(currentFile)
        return dupList
    else:
        return


# ---------- App ----------

dupList = []
delList = []

# Check for duplicated files:
for file in os.listdir(Path.cwd()):
    DupChecker(file, dupList, delList)

# Delete files in delList:
if len(delList) >= 1:
    print(f"{len(delList)} Duplicated Files:\n")
    pprint(delList)
    print()

    confirm = pyip.inputYesNo(f"Delete Duplicated Files? (y/n)")
    if confirm == "yes":
        for file in delList:
            send2trash(file)
    elif confirm == "no":
        if not os.path.isdir(Path.cwd() / "Duplicated Files"):
            os.mkdir("Duplicated Files")
        for file in delList:
            shutil.move(file, "Duplicated Files")

# Organize remaining files:
for file in os.listdir(Path.cwd()):
    if (Path.cwd() / file).suffix == "":
        continue
    elif file == "dupList.txt":
        continue
    suffix = (Path.cwd() / file).suffix
    if not os.path.isdir(Path.cwd() / suffix):
        os.mkdir(suffix)
    try:
        shutil.move(file, suffix)
    except Exception as e:
        print(e)
        if os.path.getsize(Path.cwd() / file) == os.path.getsize(Path.cwd() / suffix / file):
            send2trash(file)
            print("file deleted")
        else:
            dupList.append(file)
            print("nothing done")

# Make a .txt file with name of files with duplicated names:
today = datetime.datetime.now()
if len(dupList) > 0:
    with open("dupList.txt", "a") as dupListFile:
        dupListFile.write(f"\n-- {today.year}-{today.month}-{today.day} --\n")
        for item in dupList:
            dupListFile.write(item + "\n")
