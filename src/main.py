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

def printError(s):
    sys.stderr.write(s+"\n")


def main(args, on_success, on_error, errormsgs=None):
    global errorOut
    if errormsgs is None:
        errorOut = printError
    else:
        errorOut = on_error

    if args['analytic_data'] is not None:
        adfn = args['analytic_data']
        try:
            with open(adfn, "r") as adf:
                ConfigurationData.analytic_data = json.load(adf)
        except Exception as e:
            errorOut(adfn+": "+str(e))
            exit(1)
    elif ConfigurationData.analytic_data is None:
        if args['ansible_managed']:
            errorOut("This jaudit can not be used with Ansible as it has no built-in analytic data.")
        else:
            errorOut("No analytic data included in script. Must specify using --analytic-data option.")
        exit(1)

    #
    # To add new analytics, implement the JarIdentifier "abstract"
    # class as defined in 'jar_identifier.py', then add the python
    # source file name to ../cf/template.cf
    #
    # The analytics will be filtered based on the result of the
    # supported() method.  Those that return False, will be dropped.
    #
    # The analytic with the highest priority (priority() class method)
    # will be the default analytic.
    #
    
    all_analytics = sorted(getplugins(JarIdentifier), key=lambda a: a.priority(), reverse=True)

    State.analyticSet = list(filter(lambda a : a.supported(), all_analytics))

    if len(State.analyticSet) == 0:
        errorOut("No analytics are usable in this build.")
        return 

    commandLineError = False

    if args['list_applications']:
        apps = Configuration.get_analytic_data('enabled_apps')
        print(",".join(apps))
        return
              

    if args['list_analytics']:
        print("")
        default='*'
        for a in State.analyticSet:
            name = a.get_name()
            name = name + default
            default = ""
            if not args['full']:
                print(name)
                continue
            desc = a.get_description()
            s = ' ' * (19 - len(name))
            line=name+s
            output=""
            words = desc.split(' ')
            count = 0
            for w in words:
                n = len(w)
                if len(line)+n + 1 > 72:
                    output = output + line + "\n"
                    count = count + 1
                    line = ' ' * 19
                line = line + ' ' + w
            if len(line) > 19:
                output = output + line
                count = count + 1
            print(output)
            if count > 1:
                print("")
        print("\n  * denotes the default analytic\n")
        return

    #
    # Validate any values passed to the '-D'/'--scan-docker' option
    # Valid values are 'containers','images' and 'volumes'
    #
    dockerTests = set()
    if args['scan_docker'] is not None:
        for a in args['scan_docker']:
            if a is None:
                continue
            for v in a.split(','):
                if v in ('containers','images','volumes'):
                    dockerTests.add(v)
                else:
                    errorOut("Unrecognized value for --scan-docker: "+v)
                    commandLineError = True

    #
    # Get the names of all of the analytics
    #
    for a in State.analyticSet:
        State.analyticNames.add(a.get_name())

    #
    # Validate the enabled analytics and add them to the enabled
    # list.  If nothing was enabled, use the first analytic in the
    # set as the enabled analytic.
    #
    if args['enable'] is not None:
        for aset in args['enable']:
            if aset is None:
                continue
            for a in aset.split(','):
                if a not in State.analyticNames:
                    errorOut("Unrecognized analytic name for --enable: "+a)
                    commandLineError = True
                else:
                    State.enabledAnalytics.add(a)
    else:
        State.enabledAnalytics.add(State.analyticSet[0].get_name())

    #
    # Initialize the enabled analytics.  The initialization step is only
    # called once. It allows the analytic to do any upfront processing.
    #
    failed = set()
    for a in State.analyticSet:
        name = a.get_name()
        if name in State.enabledAnalytics:
            if not a.initialize():
                failed.add(name)

    for name in failed:
        State.enabledAnalytics.remove(name)
        errorOut("Unable to initialize analytic "+name+".")


    #
    # If any errors occurred while processing the command line, then
    # call the error processor.
    #
    if commandLineError:
        on_error(None)
        sys.exit(1)    # on_error *should* exit... but just in case

    #
    # Intialize the global state
    #
    State.verbose = args['verbose']
    if State.verbose is None:
        State.verbose = 0
    State.addEvidence = True
    if args['no_evidence'] is True:
        State.addEvidence = False

    State.scanTarFiles = args['scan_tarfiles']
    State.scanZipFiles = args['scan_zipfiles']
    
    files=args['file']

    #
    # Get a hostname and create an outer Input using the hostname
    # as the name of the Input.  All other inputs will be attached
    # to this Input.
    #
    if args['hostname'] is not None:
        hostname = args['hostname']
    else:
        hostname=gethostname()

    host=Input(hostname,"host",None)
    host.setComment("python"+sys.version[0])

    scannedFiles = set()

    #------------------------------------------------------------------------
    #
    # Scan any files provided on the command line
    #
    for fn in files:
        try:
            rn = os.path.realpath(fn)
            if rn in scannedFiles:
                continue
            inputHandle = FileInput(fn, rn, getFileType(fn))
            host.addChild(inputHandle)
            dispatchFile(inputHandle, fromUser=True)
            scannedFiles.add(rn)
            inputHandle.clean()
            inputHandle.close()
        except Exception as e:
            traceback.print_exc()
            errorOut("main1:"+str(e))

    if args['system_packages']:
        patterns=[]
        patterns.append('.*\\.jar$')
        patterns.append('.*\\.class$')
        if State.scanZipFiles:
            patterns.append(".*\\.zip$")
        if State.scanTarFiles:
            patterns.append(".*\\.tar$")
            patterns.append(".*\\.tgz$")
            patterns.append(".*\\.tar.gz$")

        pkgfiles, count = SysPackages.get_file_names(patterns)

        if pkgfiles is None:
            errorOut("System package query not supported on this platform")
        else:
            if State.verbose > 1:
                errorOut("Checking " + str(count) + " files found from system package information.")
            for ptype in pkgfiles:
                for pkg in pkgfiles[ptype]:
                    pin = Input(pkg, ptype, None)
                    host.addChild(pin)
                    for file in pkgfiles[ptype][pkg]:
                        if file in scannedFiles:
                            continue
                        if State.verbose:
                            errorOut("Scanning "+file+" from package "+pkg)
                            try:
                                inputHandle = FileInput(file, file, getFileType(file))
                                pin.addChild(inputHandle)
                                scannedFiles.add(file)
                                dispatchFile(inputHandle)
                                inputHandle.clean()
                                inputHandle.close()
                            except Exception as e:
                                errorOut("main3:"+str(e))
                    pin.clean()
        

    procInfo = ProcInfo()
    #
    # If they requested scanning running processes, check the files
    # they have open
    #
    if args['running']:
        skipargs=['-cp','-classpath']
        canGetOpenFiles = True
        for pid in procInfo.getPids():
            name = procInfo.getExecutable(pid)
            if name is None:
                continue
            if name.endswith("java") or name.endswith("java.exe"):
                id = name+"["+str(pid)+"]"
                cmdargv = procInfo.getCommandLine(pid)
                cmdline = ' '.join(cmdargv)
                progname = None
                ndx = 1
                isSameNS = procInfo.isSameNS(pid)
                cmdfiles = []
                searchPath=set()
                while ndx < len(cmdargv):
                    if len(cmdargv[ndx]) == 0:
                        ndx = ndx + 1
                        continue
                    if cmdargv[ndx] == '-jar':
                        if ndx+1 < len(cmdargv):
                            progname = cmdargv[ndx+1]
                            cmdfiles.append(progname)
                            break
                    if cmdargv[ndx] in skipargs:
                        if cmdargv[ndx] == '-cp' or cmdargv[ndx] == '-classpath':
                            if ndx+1 < len(cmdargv):
                                cp = cmdargv[ndx+1]
                                sc = ':'
                                if os.sys.platform[0:5] == 'win32':
                                    sc=';'
                                for p in cp.split(sc):
                                    if isJarFile(p):
                                        cmdfiles.append(p)
                                    elif os.path.isdir(p):
                                        searchPath.add(p)
                        ndx = ndx + 1
                    elif progname is None and cmdargv[ndx][0] != '-':
                        progname = cmdargv[ndx]
                    ndx = ndx + 1

                if progname is not None:
                    id = progname+"["+str(pid)+"]"

                pin = Input(id,"process", None)
                pin.setComment(cmdline)
                host.addChild(pin)
                if State.verbose > 0:
                    errorOut("Scanning process "+id)

                filelist = procInfo.getOpenFiles(pid)

                if filelist is None:
                    if canGetOpenFiles:
                        errorOut("openfiles command for local files is not enabled.\n\tUse: openfiles /local on\nto enable.")
                        canGetOpenFiles = False
                        continue
                scanned = set()
                for fsname,dname in filelist:
                    if os.path.isdir(fsname):
                        continue
                    if dname in scanned:
                        continue
                    scan=False
                    if isJarFile(dname) or dname.endswith(".class"):
                        scan=True
                    elif State.scanZipFiles and dname.endswith(".zip"):
                        scan=True
                    elif State.scanTarFiles and (dname.endswith(".tar") or dname.endswith(".tgz") or dname.endswith(".tar.gz")):
                        scan=True

                    if not scan:
                        continue

                    scanned.add(dname)
                    
                    try:
                        inputHandle = FileInput(fsname, dname, getFileType(dname))
                        pin.addChild(inputHandle)
                        dispatchFile(inputHandle)
                        if not isSameNS:
                            inputHandle.setName("NS(" + dname + ")")
                        inputHandle.clean()
                        inputHandle.close()
                    except Exception as e:
                        errorOut("main2:"+str(e))

                for name in cmdfiles:
                    if not os.path.exists(name):
                        for dir in searchPath:
                            if os.path.exists(dir + '/' + name):
                                name = dir + '/' + name
                                break
                    if name in scanned:
                        continue
                    scanned.add(name)
                    try:
                        inputHandle = FileInput(name, name, getFileType(name))
                        pin.addChild(inputHandle)
                        dispatchFile(inputHandle)
                        if not isSameNS:
                            inputHandle.setName("NS(" + name + ")")
                        inputHandle.clean()
                        inputHandle.close()
                    except Exception as e:
                        errorOut("main3:"+str(e))

                pin.clean()
    #
    # Create a set of file types that we consider 'local'
    #
    localFSTypes = set()
    for fs in ('ext2','ext3','ext4','vfat','fat32','ecryptfs','btrfs','xfs','jfs', 'jfs2', 'iso9660','reiserfs', 'apfs', 'zfs', 'ufs', 'removable-disk','fixed-local-disk','cdrom'):
        localFSTypes.add(fs)

    #
    # Generate a set of NON-local file systems by inverting the local
    # file system types
    #
    toSkip = set()
    fs = FileSystem()
    for fs in fs.getFileSystems(localFSTypes,invert=True):
        toSkip.add(fs)

    if args['prune_fs'] is not None:
        for pfs in args['prune_fs']:
            if pfs is None:
                continue
            for fs in pfs.split(','):
                toSkip.add(fs)

    #
    # Scan docker containers
    #
    if 'containers' in dockerTests:
        dk = Docker()
        for container in dk.getContainerList():
            p = subprocess.Popen(("docker", "export", container), stdout=subprocess.PIPE)
            inputHandle = Input(container, "docker-container", p.stdout)
            host.addChild(inputHandle)
            if State.verbose > 0:
                errorOut("Scanning docker container "+container)
            try:
                checkTar(inputHandle)
            except Exception as e:
                errorOut("main3:"+str(e))
            inputHandle.clean()
            p.wait()
    #
    # Scan docker images
    #
    if 'images' in dockerTests:
        dk = Docker()
        for image in dk.getImageList():
            p = subprocess.Popen(("docker", "save", image), stdout=subprocess.PIPE)
            inputHandle = Input(image, "docker-image", p.stdout)
            host.addChild(inputHandle)
            if State.verbose > 0:
                errorOut("Scanning docker image "+image)
            try:
                checkTar(inputHandle)
            except Exception as e:
                errorOut("main4:"+str(e))

            inputHandle.clean()
            p.wait()

    #
    # Scan docker volumes
    #
    if 'volumes' in dockerTests:
        dk = Docker()
        for volloc in dk.getVolumeList():
            name,location = volloc.split("|")
            inputHandle = Input(name, "docker-volume", None)
            host.addChild(inputHandle)
            if State.verbose > 0:
                errorOut("Scanning docker volume "+name)
            try:
                scanfs(location, toSkip, inputHandle)
            except Exception as e:
                errorOut("main5:"+str(e))
            inputHandle.clean()

    #
    # Scan any directories the user specified to scan
    #
    if args['file_system'] is not None:
        for a in args['file_system']:
            f = a.split(',')
            for fs in f:
                rfs = os.path.realpath(fs)
                if not os.path.isdir(rfs):
                    errorOut(rfs+" is not a directory; scanning as file")
                    try:
                        inputHandle = FileInput(rfs, rfs, getFileType(rfs))
                        host.addChild(inputHandle)
                        dispatchFile(inputHandle)
                        inputHandle.clean()
                        inputHandle.close()
                    except Exception as e:
                        errorOut("main6:"+str(e))

                    continue
                inputHandle = Input(rfs,"directory", None)
                host.addChild(inputHandle)
                if State.verbose > 0:
                    errorOut("Scanning directory "+rfs)
                scanfs(fs, toSkip, inputHandle)
                inputHandle.clean()
                # Avoid scanning it twice
                toSkip.add(rfs)

    #
    # If user wants to scan all mounted local file systems, then scan them
    #
    if args['search']:
        fs = FileSystem()
        toScan = list(fs.getFileSystems(localFSTypes))
        for fs in toScan:
            inputHandle = Input(fs,"file-system",None)
            host.addChild(inputHandle)
            if State.verbose > 0:
                errorOut("Scanning file system "+fs)
            skips = set()
            for s in toSkip:
                skips.add(s)
            for f in toScan:
                if f != fs:
                    skips.add(f)
            scanfs(fs, skips, inputHandle)
            inputHandle.clean()


    if len(State.looseClasses) != 0:
        cg = ClassGrouping()
        cf = cg.groupClassFiles(State.looseClasses)
        for dir in cf:
            inputHandle = Input(os.path.realpath(dir), "directory",None)
            inputHandle.setComment("Unpackaged class files")
            host.addChild(inputHandle)
            cg.classPkgVersion(cf[dir], inputHandle)
            inputHandle.clean()

    #
    # All done... everything should be in a nested data structure inside
    # of the 'host' Input... convert that to JSON and print it...
    #
    on_success(host.to_dict())

