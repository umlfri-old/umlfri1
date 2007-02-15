# setup.py
from distutils.core import setup
import py2exe
import glob
import os
import os.path
from py2exe.build_exe import py2exe as Cpy2exe
import re
from pprint import pprint

languages = {
    'sk_SK' : 'slovak'
}

reWinVar = re.compile('%(?P<env>[a-zA-Z][a-zA-Z0-9]*)%?')
def expandwinvars(path):
    while True:
        path, n = reWinVar.subn(lambda grp: os.environ[grp.group("env")], path)
        if n == 0:
            return path

def search_for_gtk():
    for path in expandwinvars(os.environ['PATH']).split(';')[::-1]:
        if os.path.isfile(os.path.join(path, 'libglib-2.0-0.dll')):
            return os.path.normpath(os.path.join(path, '..'))

class CGtkDllPy2Exe(Cpy2exe):
    GTK_PATH = search_for_gtk()
    GTK_needed_files = ['etc/fonts', 'etc/gtk-2.0', 'etc/pango', ('lib/gtk-2.0/2.4.0/engines', 'libwimp.dll'),
                        'lib/gtk-2.0/2.4.0/immodules', 'lib/gtk-2.0/2.4.0/loaders', 'lib/pango/1.4.0/modules',
                        'share/themes/MS-Windows/gtk-2.0']
    def __init__(self, *args, **kw_args):
        Cpy2exe.__init__(self, *args, **kw_args)
        self.appendGtkDlls()
    
    def appendGtkDlls(self):
        for files in self.GTK_needed_files:
            if isinstance(files, tuple):
                dir_files = [(files[0], files[1:])]
            elif isinstance(files, list):
                dir_files = []
                path = self.GTK_PATH+os.sep+files[0]
                for dirname, dirs, files in os.walk(path):
                    dir_files.append((dirname[len(self.GTK_PATH)+1:], files))
                print path
            else:
                dir_files = [(files, ("*.*", "*"))]
            for dir, files in dir_files:
                for file in files:
                    self.distribution.data_files.append((dir, glob.glob(os.sep.join((self.GTK_PATH, dir, file)))))
        for lang in languages:
            self.distribution.data_files.append(('share/locale/%s/LC_MESSAGES'%lang, glob.glob('share/locale/%s/LC_MESSAGES/*.*'%lang)))

class CInnoPy2Exe(Cpy2exe):
    def run(self):
        Cpy2exe.run(self)
        self.createInnoScript()
    
    def createInnoScript(self):
        print "*** creating the inno setup script***"
        version = self.distribution.metadata.version
        name = self.distribution.metadata.name
        url = self.distribution.metadata.url
        download_url = self.distribution.metadata.download_url
        company_name = self.distribution.metadata.author
        license = self.distribution.metadata.license
        
        if self.dist_dir[-1] not in "\\/":
            dist_dir = self.dist_dir + "\\"
        else:
            dist_dir = self.dist_dir
        
        windows_exe_files = [p[len(dist_dir):] for p in self.windows_exe_files]
        lib_files = [p[len(dist_dir):] for p in self.lib_files]
        
        pathname = dist_dir+'setup.iss'
        f = file(pathname, "w")
        print>>f, "; WARNING: This script has been created by py2exe. Changes to this script"
        print>>f, "; will be overwritten the next time py2exe is run!"
        print>>f
        print>>f, r"[Setup]"
        print>>f, r"AppName=%s"%name
        print>>f, r"AppVerName=%s %s"%(name, version)
        print>>f, r"AppPublisher=%s"%company_name
        print>>f, r"AppPublisherUrl=%s"%url
        print>>f, r"AppSupportUrl=%s"%url
        print>>f, r"AppUpdatesUrl=%s"%download_url
        print>>f, r"DefaultDirName={pf}\%s"%name
        print>>f, r"DefaultGroupName=%s"%name
        print>>f, r"AllowNoIcons=yes"
        print>>f, r"LicenseFile=%s"%license
        print>>f, r"OutputBaseFilename=setup"
        print>>f, r"Compression=lzma"
        print>>f, r"SolidCompression=yes"
        print>>f, r"PrivilegesRequired=none"
        print>>f
        
        print>>f, r"[Languages]"
        print>>f, r'Name: "english"; MessagesFile: "compiler:Default.isl"'
        for lang in languages.values():
            path = "Languages\%s.isl"%lang
            print>>f, r'Name: "%s"; MessagesFile: "compiler:%s"'%(lang, path)
        print>>f
        
        print>>f, r"[Tasks]"
        print>>f, r'Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked'
        print>>f, r'Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked'
        print>>f
        
        print>>f, r"[Files]"
        allfiles = windows_exe_files + lib_files
        allfiles.sort()
        for path in allfiles:
            dest = os.path.dirname(path)
            if dest in ('', '.'):
                dest = ''
            else:
                dest = '\\'+dest
            if path[0] == '.' and path[1] in '\\/':
                path = path[2:]
            if not os.path.isdir(os.path.join(dist_dir, path)):
                print>>f, r'Source: "%s"; DestDir: "{app}%s"; Flags: ignoreversion'%(path, dest)
        print>>f

        print>>f, r"[Icons]"
        for path in windows_exe_files:
            print>>f, r'Name: "{group}\%s"; Filename: "{app}\%s"'%(name, path)
        print>>f, r'Name: "{group}\{cm:UninstallProgram,%s}"; Filename: "{uninstallexe}"'%name
        main_exe = windows_exe_files[0]
        print>>f, r'Name: "{commondesktop}\%s"; Filename: "{app}\%s"; Tasks: desktopicon'%(name, main_exe)
        print>>f, r'Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\%s"; Filename: "{app}\%s"; Tasks: quicklaunchicon'%(name, main_exe)
        print>>f
        print>>f, r'[Run]'
        print>>f, r'Filename: "{app}\%s"; Description: "{cm:LaunchProgram,%s}"; Flags: nowait postinstall skipifsilent'%(main_exe, name)

class CGtkDllAndInnoPy2Exe(CInnoPy2Exe, CGtkDllPy2Exe):
    def __init__(self, *args, **kw_args):
        CGtkDllPy2Exe.__init__(self, *args, **kw_args)
    
    def run(self, *args, **kw_args):
        CInnoPy2Exe.run(self, *args, **kw_args)

def get_languages(path, domain):
    for lang in languages:
        p = os.path.join(path, lang, 'LC_MESSAGES')
        yield (p, [os.path.join(p, domain+'.mo')])

setup(
    name = "UML .FRI",
    description = "Free UML based CASE tool",
    version = "0.99",
    url = "http://fri.uniza.sk/",
    download_url = "http://fri.uniza.sk/",
    author = "Faculty of Management Science and Informatics, University of Zilina",
    license = "LICENSE",
    windows = [
        {
            "script": "main.py",
            "icon_resources": [(1, "doc/Logo/icon.ico")],
            "dest_base": "bin\uml_fri",
            "company_name": "Faculty of Management Science and Informatics, University of Zilina",
        }
    ],
    zipfile = 'lib/libs.dll',
    options = {
        "py2exe": {
            "includes": "pango,atk,gobject,cairo,pangocairo",
            "compressed": 1,
            "optimize": 2,
        }
    },
    data_files = [
        ("gui", glob.glob("gui/*.png")+glob.glob("gui/*.glade")),
        ("etc", glob.glob("etc/*.xml")),
        ("etc/templates", glob.glob("etc/templates/*.frit")),
        ("etc/uml/connections", glob.glob("etc/uml/connections/*.xml")),
        ("etc/uml/diagrams", glob.glob("etc/uml/diagrams/*.xml")),
        ("etc/uml/elements", glob.glob("etc/uml/elements/*.xml")),
        ("etc/uml/icons", glob.glob("etc/uml/icons/*.png")),
        ("etc/uml/versions", glob.glob("etc/uml/versions/*.xml")),
        ("img", glob.glob("img/*.png")),
        (".", ["ABOUT", "README", "LICENSE"])
    ]+list(get_languages('share/locale', 'uml_fri')),
    cmdclass = {"py2exe": CGtkDllAndInnoPy2Exe},
)