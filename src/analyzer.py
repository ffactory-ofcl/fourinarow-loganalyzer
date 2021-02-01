from re import match
from datetime import datetime


class Analyzer:
    logs: str = None

    def __init__(self, logs: str) -> None:
        self.logs = logs
        if self.logs == None:
            raise Exception('Logs must not be None!')

    def getChoices(self) -> list:
        return [
            ("Game Start Time", self.time),
            ("First Chip Placement", self.first_chip),
            ("Game Duration", self.game_duration),
        ]

    def time(self) -> None:
        title = '--  Analyzing Game Start Time  --'
        question = 'At what time of day were games requested?'
        note2 = 'This will take a while...'
        longestLen = len(question)
        print(' | {:^{len}} |'.format(title, len=longestLen))
        print(' | {:<{len}} |'.format('', len=longestLen))
        print(' | {:<{len}} |'.format(question, len=longestLen))
        print(' | {:<{len}} |'.format(note2, len=longestLen))

        # Ex: (extract time 09:43:11)
        # Dec 31 09:43:11 (...): rvm>> "MSG::4::REQ_WW"
        # Jan 01 13:49:00 (...): >> "REQ_WW"
        gameStartRegex = r'.{7}([:\d]{8}) .*?>> ".*REQ_WW"'

        times: list = []

        for msg in self.logs.splitlines():
            matchGameStart = match(gameStartRegex, msg)
            if matchGameStart != None:
                times.append(str(matchGameStart.group(1)))

        timesGrouped: dict = {}

        for hour in range(0, 24):
            for minute in range(0, 4):
                timesGrouped['{:02d}{:02d}'.format(hour, minute * 15)] = 0

        for time in times:
            timeStr = time[0:2]  # hour
            timeMinute = int(time[3:5])
            if timeMinute > 45:
                timeStr += '45'
            elif timeMinute > 30:
                timeStr += '30'
            elif timeMinute > 15:
                timeStr += '15'
            else:
                timeStr += '00'

            currentTimeGroupCount = timesGrouped[timeStr]
            timesGrouped[timeStr] = currentTimeGroupCount + 1

        totalCount = len(times)
        biggestCount = max(timesGrouped.values())
        print('Total games requested: {}'.format(totalCount))
        print()
        print('      ' + '_' * (1 + 1 * len(timesGrouped)))
        rowsCount = 16
        for row in range(rowsCount, 0, -1):
            printStr = ''
            for (time, count) in timesGrouped.items():
                printStr += '#' if count / biggestCount >= (
                    row) / rowsCount else '.'

            fractionStr = '     '
            fraction = (row / rowsCount) * (biggestCount / totalCount) * 100
            if row % 4 == 0:
                fractionStr = '{:>4.1f}'.format(fraction) + '%'
            print('{}| {} |'.format(fractionStr, printStr))

        print('      ' + '-' * (1 + 1 * len(timesGrouped)))

        printStr = ''
        for hour in range(0, 24):
            printStr += '{:02d}h '.format(hour)
        print('      ' + printStr)
        # print('  00  01  02  03  04  05  06  07  08  09')

        return

    def first_chip(self) -> None:
        title = '--  Analyzing First Chip Placement  --'
        question = 'Which of the seven columns was the first chip placed in?'
        note2 = 'This will take a little while...'
        longestLen = len(question)
        print(' | {:^{len}} |'.format(title, len=longestLen))
        print(' | {:<{len}} |'.format('', len=longestLen))
        print(' | {:<{len}} |'.format(question, len=longestLen))
        print(' | {:<{len}} |'.format(note2, len=longestLen))
        print()

        # Ex: (extract player id AAL)
        # (...) AAL<< "MSG::164::GAME_START:YOU:f63ee5679586"
        gameStartRegex = r'.*?(.{3})<< "MSG.*GAME_START:YOU.*'

        # Ex: (extract column 3)
        # (...) AAL>> "MSG::73::PC:3"
        placeChipRegex = r'.* {}>> "MSG::.+::PC:(\d)'

        columns = {
            0: 0,
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
        }

        searchingForRegex = None
        for msg in self.logs.splitlines():
            if searchingForRegex == None:
                matchGameStart = match(gameStartRegex, msg)
                if matchGameStart != None:
                    searchingForRegex = placeChipRegex.format(
                        matchGameStart.group(1))
            else:
                matchPlaceChip = match(searchingForRegex, msg)
                if matchPlaceChip != None:
                    column = int(matchPlaceChip.group(1))
                    columns[column] += 1
                    searchingForRegex = None

            pass

        totalCount = sum(columns.values())
        print("Total first chip placements: {}".format(totalCount))
        print()
        print(' ' + '_' * (2 + 3 * 7))
        rowsCount = 18
        for row in range(rowsCount, 0, -1):
            printStr = ''
            for column in columns.values():
                printStr += '# ' if column / totalCount >= row / rowsCount else '. '
                printStr += ' '
            print('|  {}|'.format(printStr))

        print(' -----------------------')
        print('   1  2  3  4  5  6  7 ')

    def game_duration(self):
        title = '--  Analyzing Game Duration  --'
        question = 'How long did the games last?'
        note = 'Not showing outliers. (shortest and longest 5%)'
        note2 = 'This will take a while...'
        longestLen = len(note)
        print(' | {:^{len}} |'.format(title, len=longestLen))
        print(' | {:<{len}} |'.format('', len=longestLen))
        print(' | {:<{len}} |'.format(question, len=longestLen))
        print(' | {:<{len}} |'.format(note, len=longestLen))
        print(' | {:<{len}} |'.format(note2, len=longestLen))
        print()

        def calculateDuration(start: str, end: str) -> int:
            '''Calculates duration in seconds between time strings of format "10:48:13"'''
            startTime = datetime(2000, 1, 1, int(start[0:2]), int(start[3:5]),
                                 int(start[6:8]))
            endTime = datetime(2000, 1, 1, int(end[0:2]), int(end[3:5]),
                               int(end[6:8]))
            return int((endTime - startTime).total_seconds())

        # Ex: (extract player id AAL)
        # (...) AAL<< "MSG::164::GAME_START:YOU:f63ee5679586"
        #
        gameStartRegex = r'.{7}([:\d]{8}) : ([\w]{3})<< "MSG::[\d]+::GAME_START:YOU'

        # Ex: (extract column 3)
        # (...) AAL>> "MSG::73::GAME_OVER:YOU:"
        gameEndRegex = (r'.{7}([:\d]{8}) : ', r'<< "MSG::[\d]+::GAME_OVER')

        gameDurations = []

        splitLines = list(
            filter(
                lambda line: line[-15:-1] == 'GAME_START:YOU' or line[-14:-5]
                == 'GAME_OVER', self.logs.splitlines(keepends=False)))

        for (index, line) in enumerate(splitLines):
            if line[25:28] != "MSG":
                # Speed hack to filter lines that won't match regex anyway
                continue

            matchGameStart = match(gameStartRegex, line)
            if matchGameStart != None:
                gameStartTimeStr = matchGameStart.group(1)
                searchingForRegex = gameEndRegex[0] + matchGameStart.group(
                    2) + gameEndRegex[1]
                for lineInner in splitLines[index:]:
                    if line[25:28] != "MSG":
                        # Speed hack to filter lines that won't match regex anyway
                        continue

                    matchGameEnd = match(searchingForRegex, lineInner)
                    if matchGameEnd != None:
                        gameEndTimeStr = matchGameEnd.group(1)
                        gameDurations.append(
                            calculateDuration(gameStartTimeStr,
                                              gameEndTimeStr))
                        break

        gameDurations = sorted(gameDurations)

        totalCount = len(gameDurations)
        percentile05index = None
        percentile95index = None
        for (index, duration) in enumerate(gameDurations):
            if index >= totalCount * 0.05 and percentile05index == None:
                percentile05index = index

            if index >= totalCount * 0.95 and percentile95index == None:
                percentile95index = index
                break

        durationsGrouped = {}

        for duration in range(gameDurations[percentile05index],
                              gameDurations[percentile95index], 10):
            durationsGrouped[duration] = 0

        for durationIndex in range(percentile05index, percentile95index):
            duration = gameDurations[durationIndex]
            lastDuration = next(iter(durationsGrouped.keys()))
            for (index, durationGrouped) in enumerate(durationsGrouped):
                if abs(duration - lastDuration) < abs(duration -
                                                      durationGrouped):
                    durationsGrouped[lastDuration] += 1
                    break
                lastDuration = durationGrouped
                if index == len(durationsGrouped) - 1:
                    durationsGrouped[lastDuration] += 1

        maxCount = max(durationsGrouped.values())
        print('Total games played: {}'.format(totalCount))
        print()
        print('      ' + '_' * (3 + 4 * len(durationsGrouped)))
        rowsCount = 16
        for row in range(rowsCount, 0, -1):
            printStr = ''
            for (duration, count) in durationsGrouped.items():
                printStr += ' #  ' if count / maxCount >= (
                    row) / rowsCount else '    '

            fractionStr = '     '
            fraction = (row / rowsCount) * (maxCount / totalCount) * 100
            if row % 4 == 0:
                fractionStr = '{:>4.1f}'.format(fraction) + '%'
            print('{}|  {} |'.format(fractionStr, printStr))

        print('      ' + '-' * (3 + 4 * len(durationsGrouped)))

        printStr = ''
        for duration in durationsGrouped.keys():
            printStr += '{:<3d} '.format(duration)
        print('         ' + printStr)
        print()
        print('      Game duration in seconds ->')
        print()
