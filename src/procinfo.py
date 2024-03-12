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


class ProcInfo:
    __sysType = None

    #
    # Add OS detection here
    #
    def __init__(self):
        platform = os.sys.platform
        if platform[0:5] == 'linux':
            self.__sysType = LinuxProcInfo()
        elif platform == 'darwin' or platform[0:3] == "aix":
            self.__sysType = MacProcInfo()
        elif platform[0:5] == 'win32':
            self.__sysType = Win32ProcInfo()
        else:
            raise NotImplementedError("No ProcInfo support for platform "+platform)

    #
    # Get list of process IDS
    #
    def getPids(self):
        '''
        Returns a list of process ids (as strings).
        '''
        return self.__sysType.getPids()
    
    #
    # Get the process environment variables as list of (key,value)
    #
    def getEnviron(self,pid):
        '''
        Returns a list of the environment variables of the given process
        identifier.  Each element of the list is a tuple consisting of the
        variable name and the variable value.
        '''
        return self.__sysType.getEnviron(pid)

    #
    # Get the command line arguments as a list
    #
    def getCommandLine(self,pid):
        '''
        Returns the command line of the specified process as a list of
        strings for each component of the command line.
        '''
        return self.__sysType.getCommandLine(pid)

    #
    # Return a list of filenames that the process has open
    #
    def getOpenFiles(self,pid):
        '''
        Returns a list containing the names of the files that the
        specified process currently has open.
        '''
        return self.__sysType.getOpenFiles(pid)

    #
    # Get the name of the executable
    #
    def getExecutable(self,pid):
        '''
        Returns the name of the file containing the executable associated
        with the given process.
        '''
        return self.__sysType.getExecutable(pid)

    #
    # Get current working directory
    #
    def getCWD(self,pid):
        '''
        Returns the current working directory of the given process.
        '''
        return self.__sysType.getCWD(pid)

    #
    # Check if process is in the same file system name space
    #
    def isSameNS(self,pid):
        '''
        Returns True if the process is in the same file system name
        space as the calling program.
        '''
        return self.__sysType.isSameNS(pid)
    

class LinuxProcInfo():

    def getPids(self):
        pids=[]
        for file in os.listdir("/proc"):
            if file.isdigit():
                pids.append(file)
        return pids

    def getEnviron(self,pid):
        env=[]
        with open("/proc/"+str(pid)+"/environ", "rb") as f:
            data = f.read()
            start = None
            end = None
            for ndx in range(0,len(data)):
                if data[ndx] == 0:
                    s = data[start:end].decode("UTF-8")
                    name,val = s.split('=',1)
                    if name.find(' ') == -1:
                        env.append((name,val))
                    start=None
                    end=None
                else:
                    if start is None:
                        start = ndx
                        end = ndx+1
                    else:
                        end = end + 1
            if start is not None:
                s = data[start:end].decode("UTF-8")
                if name.find(' ') == -1:
                    name,val = s.split('=',1)
                env.append((name,val))

        return env

    def getCommandLine(self,pid):
        args=[]
        with open("/proc/"+str(pid)+"/cmdline", "rb") as f:
            data = f.read()
            start = None
            end = None
            for ndx in range(0,len(data)):
                bd = data[ndx:ndx+1]
                b = struct.unpack('B',bd)[0]
                if b == 0:
                    args.append(data[start:end].decode("UTF-8"))
                    start=None
                    end=None
                else:
                    if start is None:
                        start = ndx
                        end = ndx+1
                    else:
                        end = end + 1
            if start is not None:
                args.append(data[start:end].decode("UTF-8"))
        if len(args) == 0:
            return None
        return args
    
    def getOpenFiles(self,pid):
        dir="/proc/"+str(pid)+"/fd"
        files=[]
        for file in os.listdir(dir):
            fsn = dir+"/"+file
            try:
                name = os.readlink(fsn)
                files.append((fsn,name))
            except:
                continue
            
        return files

    def getExecutable(self,pid):
        try:
            return os.readlink("/proc/"+str(pid)+"/exe")
        except:
            return None

    def getCWD(self,pid):
        try:
            return os.readlink("/proc/"+str(pid)+"/cwd")
        except:
            return None

    def isSameNS(self,pid):
        try :
            mine = os.readlink("/proc/self/ns/mnt")
            pids = os.readlink("/proc/"+str(pid)+"/ns/mnt")
            if mine == pids:
                return True
            return False
        except:
            return False



class MacProcInfo():

    __cache={}

    def getPids(self):
        pids=[]
        self.__cache = {}
        p = subprocess.Popen(["ps","axww"], stdout=subprocess.PIPE)
        psout=[]
        if sys.version_info.major == 3:
            with TextIOWrapper(p.stdout, encoding="utf-8") as pin:
                for line in pin:
                    psout.append(line)
        else:
            for line in p.stdout:
                psout.append(line)

        for line in psout:
            line = line.rstrip()
            line = line.strip()
            while line.find('  ') != -1:
                line = line.replace('  ',' ')
            try:
                pid, a,b,c, cmdline = line.split(' ',4)
                if pid != "PID":
                    pids.append(pid)
                    args = cmdline.split(' ')
                    self.__cache[pid] = {}
                    self.__cache[pid]['cmdline'] = args
                    self.__cache[pid]['exe'] = args[0]
            except:
                pass

        p.wait()
        
        return pids

    def getEnviron(self,pid):
        env=[]
        return env

    def getCommandLine(self,pid):
        if pid in self.__cache:
            return self.__cache[pid]['cmdline']
        return None
    
    def getOpenFiles(self,pid):
        files = []
        if os.path.exists("/usr/bin/procfiles"):
            p = subprocess.Popen(["/usr/bin/procfiles","-nc",pid], stdout=subprocess.PIPE)
            lines=[]
            if sys.version_info.major == 3:
                with TextIOWrapper(p.stdout, encoding="utf-8") as pin:
                    for line in pin:
                        lines.append(line)
            else:
                for line in p.stdout:
                    lines.append(line)
            for line in lines:
                line = line.rstrip()
                line = line.strip()
                if line.startswith("---"):
                    continue
                while line.find('  ') != -1:
                    line = line.replace('  ',' ')
                f = line.split(' ')
                if f[0] == 'FD':
                    continue
                if f[1] != '-':
                    continue
                file = f[-1]
                files.append((file,file))
            p.wait()
        elif os.path.exists("/usr/bin/lsof"):
            p=subprocess.Popen(["/usr/bin/lsof","-p",pid], stdout=subprocess.PIPE)
            lines=[]
            if sys.version_info.major == 3:
                with TextIOWrapper(p.stdout, encoding="utf-8") as pin:
                    for line in pin:
                        lines.append(line)
            else:
                for line in p.stdout:
                    lines.append(line)
            for line in lines[1:]:
                line = line.rstrip()
                line = line.strip()
                while line.find('  ') != -1:
                    line = line.replace('  ',' ')
                file = line.split(' ',8)[-1]
                files.append((file,file))
            p.wait()
        
        return files

    def getExecutable(self,pid):
        if pid in self.__cache:
            return self.__cache[pid]['exe']
        return None

    def getCWD(self,pid):
        return None

    def isSameNS(self,pid):
        return True


class Win32ProcInfo():

    __cache={}

    def getPids(self):
        pids=[]
        self.__cache = {}
        self.__haveOpenFiles = False
        p = subprocess.Popen(["C:\\Windows\\System32\\wbem\\WMIC.exe","process","get","processId,executablepath,commandline"], stdout=subprocess.PIPE)
        psout=[]
        if sys.version_info.major == 3:
            with TextIOWrapper(p.stdout) as pin:
                for line in pin:
                    psout.append(line)
        else:
            for line in p.stdout:
                psout.append(line)


        header = psout[0]

        columns={}

        start=0
        foundSpace=False
        for n in range(0,len(header)):
            if header[n] == ' ':
                if not foundSpace:
                    name = header[start:n]
                foundSpace = True
            elif foundSpace:
                columns[name]=(start,n-1)
                start = n
                foundSpace=False

        for line in psout[1:]:
            fields={}
            for fname in columns:
                (s,e) = columns[fname]
                val = line[s:e]
                val = val.rstrip()
                fields[fname] = val
            pid = fields['ProcessId']
            if pid == '':
                continue
            pids.append(pid)
            self.__cache[pid] = {}
            self.__cache[pid]['cmdline'] = fields['CommandLine'].split(' ')
            self.__cache[pid]['exe'] = fields['ExecutablePath']

        p.wait()
        
        return pids

    def getEnviron(self,pid):
        env=[]
        return env

    def getCommandLine(self,pid):
        if pid in self.__cache:
            return self.__cache[pid]['cmdline']
        return None
    
    def getOpenFiles(self,pid):
        if not self.__haveOpenFiles:
            self.__haveOpenFiles = True

            self.__openfiles = {}

            p = subprocess.Popen(["C:\\Windows\\System32\\openfiles.exe","/query","/fo","CSV","/v"], stdout=subprocess.PIPE)
            psout=[]
            if sys.version_info.major == 3:
                with TextIOWrapper(p.stdout) as pin:
                    for line in pin:
                        if line[0] == '"':
                            psout.append(line.rstrip())
            else:
                for line in p.stdout:
                    if line[0] == '"':
                        psout.append(line.rstrip())

            if len(psout) == 0:
                return None

            csvr = csv.reader(psout)
            for row in csvr:
                pid = row[2]
                filename = row[4]
                if pid not in self.__openfiles:
                    self.__openfiles[pid] = set()
                self.__openfiles[pid].add(filename)

        if pid not in self.__openfiles:
            pid = str(pid)
            if pid not in self.__openfiles:
                return []
        return [(fn,fn) for fn in self.__openfiles[pid]]

    def getExecutable(self,pid):
        if pid in self.__cache:
            return self.__cache[pid]['exe']
        return None

    def getCWD(self,pid):
        return None

    def isSameNS(self,pid):
        return True

    

