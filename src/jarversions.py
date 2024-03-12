##
## This code is part of the Jaudit utilty.
##
## (C) Copyright IBM 2023.
##
## This code is licensed under the Apache License, Version 2.0. You may
## obtain a copy of this license in the LICENSE.txt file in the root directory
## of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
##
## Any modifications or derivative works of this code must retain this
## copyright notice, and modified files need to carry a notice indicating
## that they have been altered from the originals.
##

def json_writer(record):
    print(json.dumps(record,separators=(',',':')))

def report_writer(record):
    tr = TextReport()
    tr.convert(record)
    print(tr.get())


def errorOccurred(s):
    if s is not None:
        sys.stderr.write(s+"\n")
    sys.exit(1)

if __name__ == '__main__':

    p = makeParser()
    args = vars(p.parse_args())

    if args['ansible_managed']:
        if args['report']:
            errorOccurred("Can't use --report when used with Ansible.")

    if args['check_tables_ready']:
        if ConfigurationData.analytic_data is None:
            exit(1)
        exit(0)

    writer = json_writer
    if args['report']:
        writer = report_writer
            
    try:
        main(args, writer, errorOccurred)
    except KeyboardInterrupt:
        sys.exit(1)

