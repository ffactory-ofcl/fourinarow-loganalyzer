import os
from os.path import join

from analyzer import Analyzer


def main():
    welcomeStr = "Welcome to the Four in a Row Log Analyzer by Filippo Orru (ffactory)"
    print("\n {}-".format('- ' * int(len(welcomeStr) / 2 + 1)))
    print("|  {}  |".format(welcomeStr))
    print("|  {message: ^{l}}  |".format(
        message="For more information, please refer to the readme.",
        l=len(welcomeStr)))
    print(" {}-\n".format('- ' * int(len(welcomeStr) / 2 + 1)))

    defaultFile = None
    currentDir = os.getcwd()
    for fileStr in os.listdir(currentDir):
        if fileStr.endswith('.log'):
            defaultFile = fileStr

    defaultFileStr = ""
    if defaultFile != None:
        defaultFileStr = "[Leave empty for: {}]".format(defaultFile)

    fileName = None
    logFile = None
    fileIsOkay = False
    while not fileIsOkay:
        fileName = input(
            'Which file would you like to process? {}\n  > '.format(
                defaultFileStr))

        if fileName == None or fileName == "":
            fileName = defaultFile

        if not os.path.isfile(fileName):
            print('## That is not a valid file path.')
            continue

        with open(fileName, 'r') as f:
            logFile = f.read()

        if logFile == None or len(logFile) < 100:
            print('## That file is empty or too short.')
        else:
            fileIsOkay = True
            continue

        print('Please try again.')

    print('\nOK! File loaded successfully.\n')
    analyzer = Analyzer(logFile)

    programChoice = None
    while True:
        print('Available analyzation choices:')
        choiceMethods = {}
        for (index, (choiceStr,
                     choiceMethod)) in enumerate(analyzer.getChoices()):
            choiceMethods[str(index + 1)] = choiceMethod
            print(" [{}]: {}".format(index + 1, choiceStr))

        programChoice = input('Please make a choice: ')
        print()
        choiceMethod = None
        try:
            choiceMethod = choiceMethods[programChoice]
        except KeyError:
            pass

        if choiceMethod != None:
            choiceMethod()
            print()
            print(
                "Would you like to make another analyzation? (Ctrl+C to exit)\n"
            )
        else:
            print(
                "## Not a valid choice. Please try again. (Ctrl+C to exit)\n")


if __name__ == "__main__":
    main()