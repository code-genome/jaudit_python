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

def makeParser():
    parser = argparse.ArgumentParser()

    parser.add_argument("-e", "--enable", action='append', help="Enable specific analytic; use --list-analytics for names of analytics.")
    parser.add_argument('--report', action='store_true', help="Send JSON through report generator.")
    parser.add_argument("-v", "--verbose", action='count', help="Show information about what is going on.")
    parser.add_argument("-r","--running", action='store_true', help="Analyze running processes.")
    parser.add_argument("-s", "--search", action='store_true', help="Scan mounted file systems.")
    parser.add_argument("-F", "--file-system", action='append', help="Scan a specific file-system/directory.")
    parser.add_argument("--prune-fs", action='append', help="Do not allow file system scans to scan the specified file-system/directory.")
    parser.add_argument("--analytic-data", type=str, help="Specify alternate analytic data file to load.")
    parser.add_argument("-T", "--scan-tarfiles", action='store_true', help="Scan any tar files that are discovered.")
    parser.add_argument("-Z", "--scan-zipfiles", action='store_true', help="Scan any zip files that are discovered.")
    parser.add_argument("-D", "--scan-docker", action='append', help="Scan docker containers,images or volumes.")
    parser.add_argument("--system-packages", action='store_true', help="Use system package manager to quickly locate candidate files.")
    parser.add_argument("-H", "--hostname", type=str, help="Specify the hostname to use in the output record.")
    parser.add_argument("-a", "--list-applications", action='store_true', help="List the applications that are checked.")
    parser.add_argument("--list-analytics", action='store_true', help="List the available analytics for use with --enable.")
    parser.add_argument("--full", action='store_true', help="Give full description of each analytic.")
    parser.add_argument("--no-evidence",action='store_true', help="Don't include evidence field in version records.")
    parser.add_argument('--ansible-managed', action='store_true', help="Internal option for ansible")
    parser.add_argument('--check-tables-ready', action='store_true', help="Internal option for ansible")
    parser.add_argument("file", nargs='*')
    return parser

