#!/usr/bin/env python3
# coding: utf-8

# import ssn_at
# isValid = ssn_at.validate("1237010180")
# candidates = ssn_at.generate("XXXX01011970")

import argparse, logging, csv, sys, json

def validate(ssn, stdrange=False, date=False):
    ssn = str(ssn).strip()
    print(f"{ssn!r}")
    if len(ssn) != 10:
        raise ValueError("Given social security number length is not 10")
    ssn = [int(x) for x in list(ssn)]
    if stdrange:
        if ssn[0] == 0:
            return False
    ssn_multi = list(ssn)
    ssn_multi[0] *= 3
    ssn_multi[1] *= 7
    ssn_multi[2] *= 9
    ssn_multi[3]  = 0
    ssn_multi[4] *= 5
    ssn_multi[5] *= 8
    ssn_multi[6] *= 4
    ssn_multi[7] *= 2
    ssn_multi[8] *= 1
    ssn_multi[9] *= 6
    ssn_sum = sum(ssn_multi)
    ssn_mod = ssn_sum % 11
    if ssn_mod == ssn[3]:
        return True
    else:
        return False

def generate(pattern, stdrange=True, date=True, minYear=1900, maxYear=2021):
    # untested
    if len(ssn) != 10:
        raise ValueError("Given pattern length is not 10")
    pattern = pattern.strip().casefold()
    # year
    if pattern[8:] == "xx":
        yearRange = range(minYear, maxYear)
    elif pattern[8] == "x":
        yearRange = range(int(f"190{pattern[9]}"), int(f"202{pattern[9]}"))
    elif pattern[9] == "x":
        yearRange = range(int(f"19{pattern[8]}0"), int(f"{str(maxYear)[:2]}{pattern[8]}{str(maxYear[3])}"))
    else:
        yearRange = [pattern[8:10]]
    # month
    if pattern[6:8] == "xx":
        monthRange = range(1, 13)
    elif pattern[6] == "x":
        monthRange = range(int(f"0{pattern[7]}"), int(f"1{pattern[7]}"))
    elif pattern[7] == "x":
        monthRange = range(int(f"{pattern[6]}0"), int(f"{pattern[6]}9"))
    else:
        monthRange = [pattern[6:8]]
    # day
    if pattern[4:6] == "xx":
        dayRange = range(1, 31)
    elif pattern[4] == "x":
        dayRange = range(int(f"0{pattern[5]}"), int(f"3{pattern[5]}"))
    elif pattern[5] == "x":
        dayRange = range(int(f"{pattern[4]}0"), int(f"3{pattern[4]}9"))
    else:
        dayRange = [pattern[4:6]]
    # index number
    # FIXME: muss auch parametrisierbar sein, so wie oben:
    if stdrange:
        indexRange = range(100, 1000)
    else:
        indexRange = range(0, 1000)
    if pattern[3] == "x":
        checkRange = range(0, 10)
    else:
        checkRange = [pattern[3]]
    for year in yearRange:
        for month in monthRange:
            for day in dayRange:
                if date and not _isRealDate(f"{year}-{month:0>2}-{day:0>2}"):
                    continue
                for indexNum in indexRange:
                    for checkNum in checkRange:
                        candidate = f"{indexNum}{checkNum}{day:0>2}{month:0>2}{str(year)[:3]}"
                        if validate(candidate):
                            _outputGenerated(
                                {
                                    "ssn": candidate
                                },
                                args.no_headings
                            )

def _isRealDate(datestr):
    # FIXME: pls implement
    # einfach in datetime und error catchen
    return True

def _handleMode(ssn):
    if args.mode == "validate":
        isValid = validate(ssn)
        _outputValidated(
            {
                "SSN": ssn,
                "Valid": isValid,
            },
            args.no_headings
        )
        if isValid:
            exit()
        else:
            exit(1)
    elif args.mode == "generate":
        generate(ssn)

def _outputValidated(item, noHeadings=False):
    global outputLines
    fieldnames = ["SSN", "Valid"]
    if args.csv:
        csvWriter = csv.DictWriter(
            args.outfile,
            fieldnames=fieldnames,
            delimiter=";",
            lineterminator="\n",
            extrasaction="ignore"
        )
        if outputLines == 0 and not noHeadings:
            csvWriter.writeheader()
        csvWriter.writerow(item)
    elif args.table:
        print(f"{item['SSN']}:\t{'valid' if item['valid'] else 'invalid'}")
        print()
    else:
        print(json.dumps(item), file=args.outfile)
    outputLines += 1

def _outputGenerated(item, noHeadings=False):
    global outputLines
    fieldnames = ["SSN"]
    if args.csv:
        csvWriter = csv.DictWriter(
            args.outfile,
            fieldnames=fieldnames,
            delimiter=";",
            lineterminator="\n",
            extrasaction="ignore"
        )
        if outputLines == 0 and not noHeadings:
            csvWriter.writeheader()
        csvWriter.writerow(item)
    elif args.table:
        print(f"{item['SSN']}")
        print()
    else:
        print(json.dumps(item), file=args.outfile)
    outputLines += 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(argument_default=False, description="Validate and generate social security numbers for Austrian citizens.")
    parser.add_argument("--verbose", "-v", action="count", default=0, help="Turn on verbose mode.")
    parser.add_argument("--quiet", "-q", action="store_true", help="Only return data but no log messages.")
    parser.add_argument("--log", help="Logfile path. If omitted, stdout is used.")
    parser.add_argument("--debug", "-d", action="store_true", help="Log all messages including debug.")
    parser.add_argument("--csv", action="store_true", help="Return data as CSV row.")
    parser.add_argument("--table", "-t", action="store_true", help="Output a human readable table.")
    # parser.add_argument("--validrange", action="store_true", help="Also validate range of index number.")
    # parser.add_argument("--fakedate", action="store_true", help="Allow fake dates for validation and generation of social security numbers.")
    parser.add_argument("--no-headings", action="store_true", help="Do not print CSV header.")
    parser.add_argument("--outfile", type=argparse.FileType("w", encoding="utf-8"), default=sys.stdout, help="The file in which to save the export data to.")
    parser.add_argument("mode", choices=["guess", "gen", "generate", "validate", "valid", "check", "test"], help="The mode to use. There is only validate and generate, the others are just synonyms.")
    parser.add_argument("ssn", nargs="*", help="The social security number to validate or the pattern to use for generation. Use 'XXXX' as placeholders.")
    args = parser.parse_args()

    if args.quiet:
        loglevel = 100
    elif args.debug:
        loglevel = logging.DEBUG
    elif args.verbose:
        loglevel = logging.INFO
    else:
        loglevel = logging.WARNING

    if args.log:
        logging.basicConfig(filename=args.log, filemode="a", level=loglevel)
    else:
        logging.basicConfig(level=loglevel)

    outputLines = 0
    if args.mode in ["guess", "gen", "generate"]:
        args.mode = "generate"
    elif args.mode in ["validate", "valid", "check", "test"]:
        args.mode = "validate"

    if args.ssn:
        for ssn in args.ssn:
            _handleMode(ssn)
    else:
        for line in sys.stdin:
            _handleMode(line)