import struct
import sys

from . import csidl
from nrs import fileform
from nrs.nsisfile import NSIS

DEBUG = False

REG_HKEYS = "HKCR HKCU HKLM HKU HKPD HKCC HKDD SHCTX"
HeaderAddlines = "AddBrandingImage left 100"
NSIS_COMMENT = "#"
instident = "  "
TOKENBASE = 1
CSIDLs = {
    csidl.CSIDL_WINDOWS: "WINDIR",
    csidl.CSIDL_SYSTEM: "SYSDIR",
    csidl.CSIDL_PROGRAM_FILES: "PROGRAMFILES",
    csidl.CSIDL_PROGRAMS: "SMPROGRAMS",
    csidl.CSIDL_STARTUP: "SMSTARTUP",
    csidl.CSIDL_DESKTOPDIRECTORY: "DESKTOP",
    csidl.CSIDL_STARTMENU: "STARTMENU",
    csidl.CSIDL_APPDATA: "QUICKLAUNCH",
    csidl.CSIDL_PROGRAM_FILES_COMMON: "COMMONFILES",
    csidl.CSIDL_PERSONAL: "DOCUMENTS",
    csidl.CSIDL_SENDTO: "SENDTO",
    csidl.CSIDL_RECENT: "RECENT",
    csidl.CSIDL_FAVORITES: "FAVORITES",
    csidl.CSIDL_MYMUSIC: "MUSIC",
    csidl.CSIDL_MYPICTURES: "PICTURES",
    csidl.CSIDL_MYVIDEO: "VIDEOS",
    csidl.CSIDL_NETHOOD: "NETHOOD",
    csidl.CSIDL_FONTS: "FONTS",
    csidl.CSIDL_TEMPLATES: "TEMPLATES",
    csidl.CSIDL_APPDATA: "APPDATA",
    csidl.CSIDL_LOCAL_APPDATA: "LOCALAPPDATA",
    csidl.CSIDL_PRINTHOOD: "PRINTHOOD",
    csidl.CSIDL_ALTSTARTUP: "ALTSTARTUP",
    csidl.CSIDL_INTERNET_CACHE: "INTERNET_CACHE",
    csidl.CSIDL_COOKIES: "COOKIES",
    csidl.CSIDL_HISTORY: "HISTORY",
    csidl.CSIDL_PROFILE: "PROFILE",
    csidl.CSIDL_ADMINTOOLS: "ADMINTOOLS",
    csidl.CSIDL_RESOURCES: "RESOURCES",
    csidl.CSIDL_RESOURCES_LOCALIZED: "RESOURCES_LOCALIZED",
    csidl.CSIDL_CDBURN_AREA: "CDBURN_AREA",
}

# setup\nsis-2.09-src\Source\build.cpp
#  m_UserVarNames\.add\("([^"]*)",[^/]*// (..).*
# $2 \t: '$1', \
m_UserVarNames = {
    # init with 1
    0: "0",
    1: "1",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    8: "8",
    9: "9",
    10: "R0",
    11: "R1",
    12: "R2",
    13: "R3",
    14: "R4",
    15: "R5",
    16: "R6",
    17: "R7",
    18: "R8",
    19: "R9",
    20: "CMDLINE",
    21: "INSTDIR",
    22: "OUTDIR",
    23: "EXEDIR",
    24: "LANGUAGE",  # init with -1
    25: "TEMP",
    26: "PLUGINSDIR",
    27: "EXEPATH",
    28: "EXEFILE",
    29: "HWNDPARENT",
    30: "_CLICK",  # init with 1
    31: "_OUTDIR",
}

exec_flags_autoclose = 0
exec_flags_all_user_var = 1
exec_flags_exec_error = 2
exec_flags_abort = 3
exec_flags_exec_reboot = 4
exec_flags_reboot_called = 5
exec_flags_XXX_cur_insttype = 6
exec_flags_XXX_insttype_changed = 7  # Renamed to 'exec_flags_plugin_api_version'  in ver3
exec_flags_silent = 8
exec_flags_instdir_error = 9
exec_flags_rtl = 10
exec_flags_errlvl = 11

# new in Ver3
exec_flags_alter_reg_view = 12
exec_flags_status_update = 13


class cls_Decomp:
    Sections_start = {}
    Sections_idx_To_Offset = {}
    Sections_idx = {}
    SectionsIN = {}
    Sections_end = {}
    isInsideSection = False

    Labels = {}
    Functions = {}
    isInsideFunction = False

    Tokens = {}
    Decomps = {}
    Comments = {}

    SectionTxt = {}
    DoSupress = {}

    SetOverwrite = 0  # 'on'


# for extracting ...
class FileExtract:
    CurDir = ""
    Files = []
    isUninstall = False


class EW_Tokens:
    (
        EW_INVALID_OPCODE,
        EW_RET,
        EW_NOP,
        EW_ABORT,
        EW_QUIT,
        EW_CALL,
        EW_UPDATETEXT,
        EW_SLEEP,
        EW_BRINGTOFRONT,
        EW_CHDETAILSVIEW,
        EW_SETFILEATTRIBUTES,
        EW_CREATEDIR,
        EW_IFFILEEXISTS,
        EW_SETFLAG,
        EW_IFFLAG,
        EW_GETFLAG,
        EW_RENAME,
        EW_GETFULLPATHNAME,
        EW_SEARCHPATH,
        EW_GETTEMPFILENAME,
        EW_EXTRACTFILE,
        EW_DELETEFILE,
        EW_MESSAGEBOX,
        EW_RMDIR,
        EW_STRLEN,
        EW_ASSIGNVAR,
        EW_STRCMP,
        EW_READENVSTR,
        EW_INTCMP,
        EW_INTOP,
        EW_INTFMT,
        EW_PUSHPOP,
        EW_FINDWINDOW,
        EW_SENDMESSAGE,
        EW_ISWINDOW,
        EW_GETDLGITEM,
        EW_SETCTLCOLORS,
        EW_SETBRANDINGIMAGE,
        EW_CREATEFONT,
        EW_SHOWWINDOW,
        EW_SHELLEXEC,
        EW_EXECUTE,
        EW_GETFILETIME,
        EW_GETDLLVERSION,
        EW_REGISTERDLL,
        EW_CREATESHORTCUT,
        EW_COPYFILES,
        EW_REBOOT,
        EW_WRITEINI,
        EW_READINISTR,
        EW_DELREG,
        EW_WRITEREG,
        EW_READREGSTR,
        EW_REGENUM,
        EW_FCLOSE,
        EW_FOPEN,
        EW_FPUTS,
        EW_FGETS,
        EW_FSEEK,
        EW_FINDCLOSE,
        EW_FINDNEXT,
        EW_FINDFIRST,
        EW_WRITEUNINSTALLER,
        EW_SECTIONSET,
        EW_INSTTYPESET,
        EW_GETLABELADDR,
        EW_GETFUNCTIONADDR,
        EW_LOCKWINDOW,
        EW_FPUTWS,
        EW_FGETWS,
    ) = range(0x46)

    def __init__(self):
        """Creates EW_* Names List"""
        # That get's all varNames in the class
        d = EW_Tokens.__dict__

        # Creates a dictory that will look like this: {..., 2: EW_NOP,  3: EW_ABORT, ... }
        EW_Tokens.__Names = dict((value, key) for (key, value) in d.items() if key.startswith("EW_"))
        # print(EW_Tokens.__Names)

    def Names(self, op):
        return EW_Tokens.__Names[op]


# Interesting hack to have switch/case
class switch(object):
    value = None

    def __new__(class_, value):
        class_.value = value
        return True


def case(*args):
    return any((arg == switch.value for arg in args))


def BitOptions(Flag, Names, Sep=" "):
    if type(Names) == str:
        Names = Names.split(Sep)

    StrAttributes = ""

    MaskBitselect = 1
    for bits in range(Flag.bit_length()):
        bit = Flag & MaskBitselect

        if bit:
            StrAttributes += "" if (StrAttributes == "") else Sep

            try:
                if type(Names) == dict:
                    StrAttributes += Names[bit]
                else:
                    StrAttributes += Names[bits]
            except Exception:
                StrAttributes += Sep + "0x%X" % (Flag >> bits)

        MaskBitselect <<= 1

    return StrAttributes


class Extractor:
    def __init__(self, nsis):
        self.nsis = nsis
        self.NB_STRINGS_Max = (
            nsis.header.blocks[fileform.NB_LANGTABLES].offset - nsis.header.blocks[fileform.NB_STRINGS].offset
        )
        self.UserVarNames = {}
        self.cls_Decomp = cls_Decomp()
        self.isVerNS3 = False
        self.isVerNS3 = bool(self.S(0x0011) == "CommonFilesDir")
        self.Tokenindex = 1
        self.FileExtract = FileExtract()
        self.decompFile = []

        # Config ?
        self.supressCodeOutsideSections = 0
        self.supressRawTokens = 0

    def get_NSIS_string(self, strOffset):
        # nsis-2.09-src
        NS_SKIP_CODE = 252  # 0xfc    // to consider next character as a normal character
        NS_VAR_CODE = 253  # 0xfd    // for a variable
        NS_SHELL_CODE = 254  # 0xfe    // for a shell folder path
        NS_LANG_CODE = 255  # 0xff    // for a langstring

        # nsis-3.0a2-src
        # NS_LANG_CODE  _T('\x01')
        # NS_SHELL_CODE _T('\x02')
        # NS_VAR_CODE   _T('\x03')
        # NS_SKIP_CODE  _T('\x04')

        if self.isVerNS3:
            NS_SKIP_CODE = -NS_SKIP_CODE & 0xFF
            NS_VAR_CODE = -NS_VAR_CODE & 0xFF
            NS_SHELL_CODE = -NS_SHELL_CODE & 0xFF
            NS_LANG_CODE = -NS_LANG_CODE & 0xFF

        NS_CODES_START = NS_SKIP_CODE

        if strOffset < 0:
            # TODO: re-validate that it's not already extracted for me... just in case
            # Any call to self.nsis.block should be suspicious
            strOffset = struct.unpack(
                "<i", self.nsis.block(fileform.NB_LANGTABLES)[6 - strOffset * 4 : 10 - strOffset * 4]
            )[0]

        if strOffset < self.NB_STRINGS_Max:
            string_block = self.nsis.block(fileform.NB_STRINGS)

            def MaskNewLine(data):
                # Removing vertical tabs and other non-printable characters
                if not data.isprintable():
                    return ""
                return data.replace("$", "$$").replace("\n", "$\\n").replace("\r", "$\\r").replace("\t", "$\\t")

            strData = ""
            i_offset = 0
            for i in range(strOffset * (1 + self.nsis.header.unicode), len(string_block), 1 + self.nsis.header.unicode):
                if string_block[i + i_offset] == 0x00:
                    break
                if (
                    (string_block[i + i_offset] >= NS_CODES_START)
                    if self.isVerNS3
                    else (string_block[i + i_offset] < NS_CODES_START)
                ):
                    strData += MaskNewLine(chr(string_block[i + i_offset]))
                else:
                    ns = string_block[i + i_offset]

                    if string_block[i + i_offset] == NS_SHELL_CODE:
                        ##               if isVerNS3:
                        ##                   nsCur = DECODE_SHORT(fo2, 'NS_SHELL_CODE' )
                        ##                   nsAll = nsCur
                        ##               else:

                        nsCur = struct.unpack("<B", string_block[i + i_offset + 1].to_bytes(1, "big"))[0]
                        nsAll = struct.unpack("<B", string_block[i + i_offset + 2].to_bytes(1, "big"))[0]
                        i_offset += 2

                        if nsCur & 0x80:  # and isVerNS3:
                            isX64 = nsCur & 0x40
                            is32onX64 = nsCur & 0xC0  # <= 0x80|0x40 !
                            # that is wrong or crap since it'll be always true
                            # so there's just 00..3F space left for indexing
                            retval = self.get_NSIS_string(nsCur & 0x3F)
                            # print("retval => %s" % retval)
                            if "ProgramFilesDir" == retval:
                                expanded = CSIDLs[csidl.CSIDL_PROGRAM_FILES]
                            elif "CommonFilesDir" == retval:
                                expanded = CSIDLs[csidl.CSIDL_PROGRAM_FILES_COMMON]
                            else:
                                expanded = retval + "!!<- HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\[This]!!"

                            if isX64:
                                expanded += "32" if is32onX64 else "64"
                        else:
                            try:
                                expanded = CSIDLs[nsAll]
                            except KeyError:
                                try:
                                    expanded = CSIDLs[nsCur]
                                except KeyError:
                                    expanded = "Unknown_CSIDL_%X_or_%X" % (nsAll, nsCur)

                        # print('%s' % expanded)
                        strData += "$" + expanded
                    elif ns == NS_VAR_CODE:
                        A = struct.unpack("<B", string_block[i + i_offset + 1].to_bytes(1, "big"))[0]
                        B = struct.unpack("<B", string_block[i + i_offset + 2].to_bytes(1, "big"))[0]
                        i_offset += 2
                        nData = ((B & ~0x80) << 7) | (A & ~0x80)
                        strData += self.GetUserVarName(nData)
                    elif ns == NS_LANG_CODE:
                        # nData = DECODE_SHORT(fo2, 'NS_LANG_CODE' )
                        A = struct.unpack("<B", string_block[i + i_offset + 1].to_bytes(1, "big"))[0]
                        B = struct.unpack("<B", string_block[i + i_offset + 2].to_bytes(1, "big"))[0]
                        i_offset += 2
                        nData = ((B & ~0x80) << 7) | (A & ~0x80)
                        if B & 0x80:
                            retval = self.get_NSIS_string(-nData - 1)
                            # print("retval => %s" % retval)
                            strData += retval
                        else:
                            raise Exception("NSIS_SETUP.get_NSIS_string: How do we get in here? Anything to do?")
                            fo2.seek(-2, os.SEEK_CUR)
                            # strData += chr(A) + chr(B)
                        # stop

                    elif ns == NS_SKIP_CODE:
                        # 0xfc that's the german 'ü'
                        # print("NS_SKIP_CODE")
                        strData += MaskNewLine(chr(string_block[i + i_offset + 1]))

            return strData

    def B(self, data):
        if self.isVerNS3:
            return repr(self.get_NSIS_string(data))
        else:
            return hex(data)

    def S(self, data, Prefix="", Postfix=""):
        return self.add_string(data, Prefix, Postfix)

    # Quote Empty stringd
    def Sq(self, data, Prefix=""):
        tmp = self.add_string(data, Prefix)
        if tmp == "":
            return '""'
        else:
            return tmp

    def S_Int(self, data, Prefix="", Postfix=""):
        return self.add_intstring(data, Prefix, Postfix)

    def add_intstring(self, data, Prefix="", Postfix=""):
        try:
            return int(self.S(data, Prefix, Postfix))
        except ValueError:
            if data == 0:
                return 0
            else:
                raise (ValueError)

    def add_string(self, data, Prefix="", Postfix=""):
        return self.quoteStringIfNeeded(Prefix + self.get_NSIS_string(data) + Postfix)

    def quoteStringIfNeeded(self, data):
        hasSpace = " " in data
        hasDash = "#" in data
        isKeyword = "section" in data.lower()
        if hasSpace or hasDash or isKeyword:
            return self.quoteString(data)
        else:
            return data

    def quoteString(self, data):
        hasSingleQ = "'" in data
        hasSingleBwQ = "`" in data
        hasDoubleQ = '"' in data
        if hasSingleBwQ and hasSingleQ and hasDoubleQ:
            # if '$' in data:
            #    data = data.replace('$','$$')
            return '"%s"' % data.replace('"', '$\\"')
        elif hasSingleQ and hasDoubleQ:
            return "`%s`" % data
        elif hasSingleQ:
            return '"%s"' % data
        else:
            return "'%s'" % data

    def MB_Style(self, parm):
        # 0..5
        MB = []
        MB.append(
            self.getnumtokens(parm & 7, "MB_OK MB_OKCANCEL MB_ABORTRETRYIGNORE MB_YESNOCANCEL MB_YESNO MB_RETRYCANCEL")
        )

        # 16 32 48 64
        bits = (parm >> 4) & 7
        if bits:
            MB.append(self.getnumtokens(bits, " MB_ICONSTOP MB_ICONQUESTION MB_ICONEXCLAMATION MB_ICONINFORMATION"))

        MB_USERICON = 0x80
        if parm & MB_USERICON:
            MB.append("MB_USERICON")

            #  define MB_SETFOREGROUND   0x10000
            #  define MB_TOPMOST         0x40000
            #  define MB_RIGHT           0x80000
            #  define MB_RTLREADING     0x100000
        bits = (parm >> 16) & 7
        if bits:
            MB.append(BitOptions(bits & 7, "MB_SETFOREGROUND MB_TOPMOST MB_RIGHT MB_RTLREADING"))

        # TODO: Hopefully that's still the same??
        # Rest = (parm0 & ~( 7<<16 | 017<<4 | 7))
        Rest = parm & ~(7 << 16 | 0o17 << 4 | 7)
        if Rest:
            MB.append(hex(Rest))

        return "|".join(MB)

    def E(self, data, Enum="", PreFix_NotFound=""):
        return self.getnumtokens(data, Enum, PreFix_NotFound)

    def getnumtokens(self, data, Enum="", PreFix_NotFound=""):
        try:
            index = int(self.S(data))
        except Exception:
            # TODO: Add that as a DecompComment?
            # print("NSIS_SETUP.getnumtokens: Whoops using data directly as enum idx.")
            index = data

        try:
            EnumList = Enum.split(" ")
            return EnumList[index]
        except IndexError:
            # TODO: Add that as a DecompComment?
            # print(f"NSIS_SETUP.getnumtokens: Select EnumMember '{index}' fail - plz do it manually from this list: {Enum}")
            return PreFix_NotFound + "%i" % index

    def F(self, data):
        return self.ns_func(data, "func")

    def JJ(self, yes, no):
        return self.LL(yes, no)

    def J(self, data):
        #    return self.L(data)
        return self.process_jump(data)

    def process_jump(self, data):
        if data <= 0:
            return ""

        TokenRelatively = data - self.Tokenindex

        # TODO: Check if the comment would be worth the refactoring
        # global DecompComment
        # DecompComment += " Or 0x%x " % data

        return "%+i" % TokenRelatively
        # return GetNSISString( data )

    def LL(self, yes, no):
        if no:
            return "%s %s" % (self.ns_label(yes, 0), self.ns_label(no))
        else:
            return self.ns_label(yes)

    def L(self, data):
        return self.ns_label(data)

    def ns_func(self, data, Prefix="", Offset=0, AppendOffset=True):
        # create Label Text
        if type(data) == str:
            if Offset < 0:  # TODO .. or Entries[Offset] == EW_RET
                return '""'
            FuncText = "%s%s" % (Prefix, data)
            if AppendOffset:
                FuncText += "_%X" % Offset

            data = Offset
        else:
            if data < 0:
                FuncText = self.GetUserVarName(~data)
            else:
                # FuncText = "%s_0x%X" % (Prefix, data)
                FuncText = "%s_%i" % (Prefix, data - 1)

        # Store in
        # TODO: Check if that's really the fix?
        self.cls_Decomp.Functions[data] = "Function " + FuncText
        # self.cls_Decomp.Functions[data + TOKENBASE] = "Function " + FuncText

        return FuncText

    def ns_label(self, data, Empty="", Prefix="label"):  # Prefix="Label"):
        if data:
            # create Label Text
            # LabelText = "%s_0x%X" % (Prefix, data)
            LabelText = "%s_%i" % (Prefix, data - 1)

            # Store in Labels
            self.cls_Decomp.Labels[data] = LabelText + ":"
        else:
            LabelText = Empty

        return LabelText

    def SECTION_FIELD(self, data):
        data = self.get_NSIS_string(data)
        SectidxName = "Section_%s" % data
        Offset = self.cls_Decomp.Sections_idx_To_Offset[int(data)]
        self.cls_Decomp.Sections_idx[Offset] = SectidxName
        return "${" + SectidxName + "}"

    # Renamed from I from ambiguosity with variable named I.
    def II(self, data, Prefix="", SkipIfNull=False):
        return self.gettoken_int(data, Prefix, SkipIfNull)

    def gettoken_int(self, data, Prefix="", SkipIfNull=False):
        if data or not SkipIfNull:
            return Prefix + "%i" % data
        else:
            return ""

    def V(self, data):
        return self.GetUserVarName(data)

    def GetUserVarName(self, nData):
        if nData < 0:
            return self.get_NSIS_string(nData)

        staticUserVars = len(m_UserVarNames)
        # expanded = ''
        # -1 because first item in dict is 1: (and not 0:)
        if nData in range(0, staticUserVars - 1):
            return "$" + m_UserVarNames[nData]
        else:
            return self.MakeUserVarName(nData - staticUserVars)

    def MakeUserVarName(self, num):
        UserVarName = f"_{num}_"  # "UserVar%i" % num

        # Track if declared
        if num in self.UserVarNames:
            pass
        else:
            self.decompFile.append("Var %s" % UserVarName)
            self.UserVarNames[num] = UserVarName

        return "$" + UserVarName

    def dumpPages(self):
        for page in self.nsis.pages:
            wndproc_id = page.wndproc_id
            p_id = "%i" % wndproc_id
            if wndproc_id > 4:
                PageName = "custom"
            else:
                PageName = self.E(wndproc_id + 1, "custom license components directory instfiles uninstConfirm")

            prefuncText = self.ns_func(("pre_page" + p_id) if page.dlg_id else "create_page" + p_id, "", page.prefunc)
            showfuncText = self.ns_func("show_page" + p_id, "", page.showfunc)
            leavefuncText = self.ns_func("leave_page" + p_id, "", page.leavefunc)
            captiontext = self.S(page.caption)

            isNotLastPage = True  # (page < NB_PAGES_Num-1)
            if isNotLastPage and page.dlg_id >= 0:
                self.decompFile.append(
                    "Page %s %s %s %s ; %s"
                    % (PageName, prefuncText, "" if PageName == "custom" else showfuncText, leavefuncText, captiontext)
                )
                for param in page.params:
                    if param != 0x00:
                        self.decompFile.append(instident + self.S(param))
                self.decompFile.append("")

            if DEBUG:
                print("dlg_id: 0x%.4X" % (page.dlg_id))
                print("wndproc_id: 0x%.4X -> %s" % (page.wndproc_id, PageName))
                print("prefunc: 0x%.4X %s" % (page.prefunc, prefuncText))
                print("showfunc: 0x%.4X %s" % (page.showfunc, showfuncText))
                print("leavefunc: 0x%.4X %s" % (page.leavefunc, leavefuncText))
                print("flags: 0x%.4X" % (page.flags))
                print("caption: 0x%.4X - %s" % (page.caption, captiontext))
                print("back: 0x%.4X - %s" % (page.back, ""))
                print("next: 0x%.4X - %s" % (page.next, ""))
                print("clicknext: 0x%.4X - %s" % (page.clicknext, ""))
                print("cancel: 0x%.4X - %s" % (page.cancel, ""))
                print("parms0: 0x%.4X - %s" % (page.params[0], ""))
                print("parms1: 0x%.4X - %s" % (page.params[1], ""))
                print("parms2: 0x%.4X - %s" % (page.params[2], ""))
                print("parms3: 0x%.4X - %s" % (page.params[3], ""))
                print("parms4: 0x%.4X - %s" % (page.params[4], ""))
                print()

    def DumpInstTypes(self):
        InstType = []
        # InstType from 0..31
        for item in self.nsis.header.install_types[:-1]:
            if item != 0:
                v = ""
                try:
                    v = self.S(item)
                    InstType.append(v)
                except Exception:
                    pass

        # Custom (32)
        try:
            v = self.S(self.nsis.header.install_types[-1])
            if v != "Custom":
                InstType.append("/CUSTOMSTRING=%s" % v)
        except Exception:
            pass

        if self.nsis.header.flags & fileform.CH_FLAGS_NO_CUSTOM:
            InstType.append("/NOCUSTOM")

        if self.nsis.header.flags & fileform.CH_FLAGS_COMP_ONLY_ON_CUSTOM:
            InstType.append("/COMPONENTSONLYONCUSTOM")

        return InstType

    def dumpSections(self):
        for i, section in enumerate(self.nsis.sections):
            # Flags bit values
            SF_SELECTED = 1
            SF_SECGRP = 2
            SF_SECGRPEND = 4
            SF_BOLD = 8
            SF_RO = 0x10
            SF_EXPAND = 0x20
            SF_PSELECTED = 0x40
            SF_TOGGLED = 0x80
            SF_NAMECHG = 0x100

            name = self.S(section.name_ptr, "!" if section.flags & SF_BOLD else "")

            SF_Group = "Group" if (section.flags & (SF_SECGRP | SF_SECGRPEND)) else ""

            SF_Options = ""
            if section.flags & SF_EXPAND:
                SF_Options += "/e "

            if not (section.flags & SF_SELECTED):
                SF_Options += "/o "

            Section = "Section" + SF_Group + " " + SF_Options + name

            SectionIn = (
                "SectionIn "
                + BitOptions(section.install_types, ["%i" % num for num in range(1, 32)])
                + (" RO" if section.flags & SF_RO else "")
            )

            if not (section.flags & SF_SECGRPEND):
                self.cls_Decomp.Sections_start[section.code] = Section
                if section.install_types and (name != ""):
                    self.cls_Decomp.SectionsIN[section.code] = SectionIn
                # +1 is stupid fix for 'return' outside section
                self.cls_Decomp.Sections_end[section.code + section.code_size + 1] = "Section" + SF_Group + "End\n\n"

            # That is just to find the Section by idx
            self.cls_Decomp.Sections_idx_To_Offset[i] = section.code

            if DEBUG:
                flags_text = BitOptions(
                    section.flags,
                    "SF_SELECTED"
                    "SF_SECGRP"
                    "SF_SECGRPEND"
                    "SF_BOLD"
                    "SF_RO"
                    "SF_EXPAND"
                    "SF_PSELECTED"
                    "SF_TOGGLED"
                    "SF_NAMECHG",
                    "\n",
                )

                print("  name_ptr: 0x%.4X - %s" % (section.name_ptr, name))
                print("  install_types: 0x%.4X" % section.install_types)
                print("  flags: 0x%.4X - flags_text: %s" % (section.flags, flags_text))
                print(
                    "  code: 0x%.4X size: 0x%.4X => end: 0x%.4X"
                    % (section.code, section.code_size, section.code + section.code_size)
                )
                print("  size_kb: %i" % section.size_kb)
                print("  invisible_sections (\\x00 stripped): %s" % section.name.strip(b"\x00"))
                print("---------------------------")

    def ProcessEntries(self):
        e = EW_Tokens()
        for i, entry in enumerate(self.nsis.entries, start=TOKENBASE):
            self.Tokenindex = i

            Decomp = ""
            DecompComment = ""
            skipCommand = False
            which_Name = e.Names(entry.which)
            parm0 = entry.offsets[0]
            parm1 = entry.offsets[1]
            parm2 = entry.offsets[2]
            parm3 = entry.offsets[3]
            parm4 = entry.offsets[4]
            parm5 = entry.offsets[5]

            def R(Num):
                return "%4X" % Num if Num else "%4s" % "-"

            lineRawInfo = "#%4.3X %.2X_%16s" % (i, entry.which, which_Name)
            if parm0 | parm1 | parm2 | parm3 | parm4 | parm5:
                lineRawInfo += " : %s %s %s %s %s %s" % (R(parm0), R(parm1), R(parm2), R(parm3), R(parm4), R(parm5))

            if DEBUG:
                print("       " + lineRawInfo)

            while switch(entry.which):
                if case(e.EW_WRITEINI):
                    if parm4 == 1:
                        Decomp = "WriteINIStr %s %s %s %s" % (
                            self.S(parm3),
                            self.S(parm0),
                            self.S(parm1),
                            self.Sq(parm2),
                        )
                    elif (parm2 == 0) and (parm1 != 0):
                        Decomp = "DeleteINIStr  %s %s %s" % (self.S(parm3), self.S(parm0), self.S(parm1))
                    elif (parm1 == 0) and (parm0 != 0):
                        Decomp = "DeleteINISec  %s %s" % (self.S(parm3), self.S(parm0))
                    else:
                        Decomp = "FlushINI %s " % self.S(parm3)
                    break
                if case(e.EW_ASSIGNVAR):
                    isGetCurrentAddress = False
                    try:
                        isGetCurrentAddress = self.S_Int(parm1) == self.Tokenindex
                    except Exception:
                        pass
                    if isGetCurrentAddress:
                        Decomp = "GetCurrentAddress %s" % self.V(parm0)
                    else:
                        Decomp = "StrCpy %s %s %s %s" % (self.V(parm0), self.Sq(parm1), self.S(parm2), self.S(parm3))
                        if self.V(parm0) == "$PLUGINSDIR":
                            DecompComment += '<-that\'ll give a compile error! Anyway delete whole function and replace calls with a simple "InitPluginsDir" '
                    break
                if case(e.EW_READREGSTR):
                    if parm4 == 0:
                        CmdName = "Str"
                    elif parm4 == 1:
                        CmdName = "DWORD"
                    else:
                        CmdName = "ERRoR!!!"
                    # "HKCR HKLM HKCU HKU HKCC HKDD HKPD SHCTX" <- original order
                    # "HKCR HKCU HKLM HKU HKPD HKCC HKDD SHCTX" <- Reordered so it's 0x80000000..6
                    Decomp = "ReadReg%s %s %s %s %s" % (
                        CmdName,
                        self.V(parm0),
                        self.E(parm1 & 0xF, "HKCR HKCU HKLM HKU HKPD HKCC HKDD SHCTX"),
                        self.S(parm2),
                        self.S(parm3),
                    )
                    break
                if case(e.EW_WRITEREG):
                    REG_SZ = 1
                    REG_EXPAND_SZ = 2
                    REG_BINARY = 3
                    REG_DWORD = 4
                    data = self.S(parm3)
                    if parm5 == REG_SZ:
                        CmdName = "Str"
                    elif parm5 == REG_EXPAND_SZ:
                        CmdName = "ExpandStr"
                    elif parm5 == REG_BINARY:
                        CmdName = "Bin"
                        data = self.B(parm3)
                    elif parm5 == REG_DWORD:
                        CmdName = "DWORD"
                    # "HKCR HKLM HKCU HKU HKCC HKDD HKPD SHCTX" <- original order
                    # "HKCR HKCU HKLM HKU HKPD HKCC HKDD SHCTX" <- Reordered so it's 0x80000000..6
                    Decomp = "WriteReg%s %s %s %s %s" % (
                        CmdName,
                        self.E(parm0 & 0xF, REG_HKEYS),
                        self.Sq(parm1),
                        self.Sq(parm2),
                        data,
                    )
                    break
                if case(e.EW_DELREG):
                    if parm3 == 0:
                        CmdName = "Key"  # and param4 in (1,3)
                    else:
                        CmdName = "Value"
                    # REG_HKEYS
                    # "HKCR HKLM HKCU HKU HKCC HKDD HKPD SHCTX" <- original order
                    # "HKCR HKCU HKLM HKU HKPD HKCC HKDD SHCTX" <- Reordered so it's 0x80000000..6
                    Decomp = "DeleteReg%s %s %s %s %s" % (
                        CmdName,
                        self.E(parm1 & 0xF, REG_HKEYS),
                        self.Sq(parm2),
                        self.S(parm3),
                        "/ifempty" if parm4 == 3 else "",
                    )
                    break
                if case(e.EW_READINISTR):
                    Decomp = "ReadINIStr %s %s %s %s" % (self.V(parm0), self.S(parm3), self.S(parm1), self.S(parm2))
                    break
                if case(e.EW_FOPEN):
                    # parm1
                    # define GENERIC_READ  0x8000 0000
                    # define GENERIC_WRITE 0x4000 0000
                    # parm1>>29

                    # parm2
                    #  CREATE_NEW    1
                    #  CREATE_ALWAYS 2 w
                    #  OPEN_EXISTING 3 r
                    #  OPEN_ALWAYS   4 a
                    openmode = self.E(parm2 - 2, "r w a")
                    Decomp = "FileOpen %s %s %s" % (
                        self.V(parm0),
                        self.S(parm3),
                        openmode,
                    )
                    break
                if case(e.EW_FCLOSE):
                    Decomp = "FileClose %s" % self.V(parm0)
                    break
                if case(e.EW_FGETS):
                    if parm3 == 1:
                        cmdext = "Byte"
                        FR_size = ""
                    else:
                        cmdext = ""
                        FR_size = self.S(parm2)
                    Decomp = "FileRead%s %s %s %s" % (cmdext, self.V(parm0), self.V(parm1), FR_size)
                    break
                if case(e.EW_FPUTS):
                    cmdext = "Byte" if parm2 == 1 else ""
                    Decomp = "FileWrite%s %s %s" % (cmdext, self.V(parm0), self.S(parm1))
                    break
                if case(e.EW_FGETWS):
                    if parm3 == 1:
                        cmdext = "Word"
                        FR_size = ""
                    else:
                        cmdext = "UTF16LE"
                        FR_size = self.S(parm2)
                    Decomp = "FileRead%s %s %s %s" % (cmdext, self.V(parm0), self.V(parm1), FR_size)
                    break
                if case(e.EW_FPUTWS):
                    cmdext = "Word" if parm2 == 1 else "UTF16LE"
                    Decomp = "FileWrite%s %s %s" % (cmdext, self.V(parm0), self.S(parm1))
                    break
                if case(e.EW_FSEEK):
                    # TODO: Why is parm1 showing up here and not in 7z?
                    Decomp = "FileSeek %s %s %s %s" % (
                        self.V(parm0),
                        self.S(parm2),
                        self.E(parm3, " CUR END"),
                        self.V(parm1),
                    )
                    # Note SET is default
                    break
                if case(e.EW_FINDFIRST):
                    Decomp = "FindFirst %s %s %s" % (self.V(parm1), self.V(parm0), self.S(parm2))
                    break
                if case(e.EW_FINDNEXT):
                    Decomp = "FindNext %s %s" % (self.V(parm1), self.V(parm0))
                    break
                if case(e.EW_FINDCLOSE):
                    Decomp = "FindClose %s" % (self.V(parm0))
                    break
                if case(e.EW_WRITEUNINSTALLER):
                    global CommentOutWriteUninstaller
                    Decomp = (NSIS_COMMENT if CommentOutWriteUninstaller else "") + "WriteUninstaller %s" % self.S(
                        parm0
                    )
                    DecompComment = "Offset: %x  Iconstyle: %x  More: %s" % (parm1, parm2, self.S(parm3))
                    break
                if case(e.EW_CREATESHORTCUT):

                    # parm4 bitlayout
                    #    0  IconIndex
                    #    8  ShowState
                    #   16  HotKey
                    #   24  FKey
                    import ctypes

                    c_uint8 = ctypes.c_uint8

                    class EW_CREATESHORTCUT_Flags_bits(ctypes.LittleEndianStructure):
                        _fields_ = [
                            ("IconIndex", c_uint8, 8),  # 0
                            ("ShowState", c_uint8, 3),  # 8
                            ("Filler1", c_uint8, 5),
                            ("HotKey_key", c_uint8, 8),  # 16
                            ("HotKey_mod", c_uint8, 8),  # 24
                        ]

                    class EW_CREATESHORTCUT_Flags(ctypes.Union):
                        _fields_ = [
                            ("b", EW_CREATESHORTCUT_Flags_bits),
                            ("asByte", c_uint8),
                            ("asInt32", ctypes.c_uint32),
                        ]
                        _anonymous_ = "b"

                    HOTKEYF_SHIFT = 1
                    HOTKEYF_CONTROL = 2
                    HOTKEYF_ALT = 4
                    HOTKEYF_EXT = 8
                    VK_F1 = 0x70

                    parm4_opt = EW_CREATESHORTCUT_Flags()
                    parm4_opt.asInt32 = parm4

                    hotkeys_int = parm4_opt.HotKey_mod  # parm4 >> 24
                    hotkeys = ""
                    if hotkeys_int & HOTKEYF_ALT:
                        hotkeys += "ALT|"
                    if hotkeys_int & HOTKEYF_CONTROL:
                        hotkeys += "CONTROL|"
                    if hotkeys_int & HOTKEYF_SHIFT:
                        hotkeys += "SHIFT|"
                    if hotkeys_int & HOTKEYF_EXT:
                        hotkeys += "EXT|"

                    FKey = parm4_opt.HotKey_key  # (parm4 >> 16 ) & 0xff
                    if FKey >= VK_F1:
                        FKey -= VK_F1 - 1

                        FKey = "F" + str(FKey)
                    else:
                        if FKey in range(0x20, 0x7F):
                            FKey = chr(FKey)

                    if FKey == 0:
                        FKey = ""

                    # icon_index_number = parm4 & 0xff
                    CommandlineParameters = self.Sq(parm2)
                    icon_file = self.Sq(parm3)
                    description = self.S(parm5)
                    Decomp = "CreateShortCut %s %s %s %s %s %s %s%s %s" % (
                        self.Sq(parm0),
                        self.Sq(parm1),
                        CommandlineParameters,
                        icon_file,
                        self.II(parm4_opt.IconIndex),  # TODO: Where is I from?
                        self.E(parm4_opt.ShowState, " SW_SHOWNORMAL  SW_SHOWMAXIMIZED    SW_SHOWMINIMIZED"),
                        hotkeys,
                        FKey,
                        description,
                    )
                    # ent.offsets[4]=1; // write
                    break
                if case(e.EW_CREATEDIR):
                    op = self.S(parm0)
                    if parm1 == 1:
                        # if op=="$INSTDIR":
                        #   op='"-"'
                        Decomp = "SetOutPath %s " % op
                        self.FileExtract.CurDir = op
                    else:
                        Decomp = "CreateDirectory %s " % op
                    break
                if case(e.EW_INVALID_OPCODE):
                    DecompComment = "INVALID_OPCODE:%x @ 0x%X" % (e.EW_INVALID_OPCODE, self.Tokenindex)
                    break
                if case(e.EW_UPDATETEXT):
                    Decomp = "DetailPrint %s " % self.Sq(parm0)
                    break
                if case(e.EW_CREATEDIR):
                    Decomp = "CreateDirectory %s" % self.S(parm0)
                    break
                if case(e.EW_STRLEN):
                    Decomp = "StrLen %s %s " % (self.V(parm0), self.S(parm1))
                    break
                if case(e.EW_INTOP):
                    op1 = self.S(parm1)
                    op2 = self.S(parm2)
                    op = self.E(parm3, "+ - * / | & ^ ! || && % << >> ~ ")
                    if (op == "^") and (op2 == "0xFFFFFFFF"):
                        op = "~"
                        op2 = ""
                    Decomp = "IntOp %s %s %s %s" % (self.V(parm0), op1, op, op2)
                    break
                if case(e.EW_INTCMP):
                    # "a" "b" is less more
                    # catch undocumented Label use parm2 <, parm3 = , parm4 >
                    # assert parm3==0
                    Decomp = (
                        "IntCmp"
                        + ("U" if parm5 else "")
                        + " %s %s %s %s" % (self.Sq(parm0), self.Sq(parm1), self.J(parm2), self.JJ(parm3, parm4))
                    )
                    break
                if case(e.EW_STRCMP):
                    # catch undocumented Label use parm2 <, parm3 = , parm4 >
                    # assert parm4==0
                    Decomp = "StrCmp%s %s %s %s %s" % (
                        "S" if parm5 == 1 else "",
                        self.Sq(parm0),
                        self.Sq(parm1),
                        self.JJ(parm2, parm3),
                        self.J(parm4),
                    )
                    break
                if case(e.EW_RET):
                    DecompComment = "Return"
                    if self.supressCodeOutsideSections:
                        skipCommand = True
                    # if cls_Decomp.isInsideFunction:
                    # cls_Decomp.Functions[i] = ";FunctionEnd\n"
                    # cls_Decomp.isInsideFunction = False
                    break
                if case(e.EW_SLEEP):
                    Decomp = "Sleep %s" % self.S(parm0)
                    break
                if case(e.EW_LOCKWINDOW):
                    Decomp = "LockWindow %s" % self.E(parm0, "on off")
                    break
                if case(e.EW_BRINGTOFRONT):
                    Decomp = "BringToFront"
                    break
                if case(e.EW_QUIT):
                    Decomp = "Quit"
                    break
                if case(e.EW_ABORT):
                    Decomp = "Abort %s" % self.S(parm0)
                    break
                if case(e.EW_REBOOT):
                    Decomp = "Reboot"
                    if parm0 != 0xBADF00D:
                        DecompComment = "Installation corrupted"
                    break
                if case(e.EW_SEARCHPATH):
                    Decomp = "SearchPath %s %s" % (self.V(parm0), self.S(parm1))
                    break
                if case(e.EW_NOP):
                    if parm0 == 0:
                        Decomp = "Nop"
                    else:
                        Decomp = "Goto %s" % self.L(parm0)
                    break
                if case(e.EW_PUSHPOP):
                    if parm1 == 0:
                        if parm2 == 0:
                            Decomp = "Push %s" % self.S(parm0)
                        else:
                            Decomp = "Exch %s" % self.II(parm2)
                            DecompComment = "TODO: Check Push/POP around this. Maybe remove them!"
                    else:
                        Decomp = "Pop %s" % self.V(parm0)
                    break
                if case(e.EW_SETCTLCOLORS):
                    Decomp = "SetCtlColors %s %s %s" % (self.S(parm0), self.Sq(parm1), self.S(parm2))
                    DecompComment = "Warning: SetCtlColors is not completely implemented"
                    break
                if case(e.EW_SETBRANDINGIMAGE):
                    # IDD_INST                        105
                    # CONTROL "", 1046, "STATIC", SS_BITMAP, 0, 0, 100, 35
                    # IDC_BRANDIMAGE
                    # NeedsAddBrandingImage = True
                    Decomp = "SetBrandingImage /IMGID=%i %s %s" % (
                        parm1,
                        "/RESIZETOFIT" if parm2 else "",
                        self.get_NSIS_string(parm0),
                    )
                    DecompComment = 'you may need to "AddBrandingImage left 100" or sth at the beginning - exact data for the is in .rsrc\DLG_105:1033[SS_BITMAP]; brandingCtl.sHeight = wh brandingCtl.sX = padding; (left|right|top|bottom)'
                    break
                if case(e.EW_GETFUNCTIONADDR):
                    Decomp = "GetFunctionAddress %s %s" % (self.V(parm0), self.F(parm1))
                    break
                if case(e.EW_CALL):
                    if parm1 == 1:
                        # isLabel
                        Decomp = "Call :%s" % self.L(parm0)
                    else:
                        Decomp = "Call %s" % self.F(parm0)
                    break
                if case(e.EW_GETTEMPFILENAME):
                    base_dir = self.S(parm1)
                    Decomp = "GetTempFileName %s %s" % (
                        self.V(parm0),
                        base_dir if (base_dir.upper() != "$TEMP") else "",
                    )
                    break
                if case(e.EW_GETDLLVERSION):
                    Decomp = "GetDLLVersion %s %s %s" % (self.S(parm2), self.V(parm0), self.V(parm1))
                    break
                if case(e.EW_GETDLGITEM):
                    Decomp = "GetDlgItem %s %s %s" % (self.V(parm0), self.S(parm1), self.S(parm2))
                    break
                if case(e.EW_IFFILEEXISTS):
                    Decomp = "IfFileExists  %s %s" % (self.S(parm0), self.JJ(parm1, parm2))
                    break
                if case(e.EW_IFFLAG):
                    if parm2 == exec_flags_exec_error:
                        Decomp = "IfErrors"
                        # if param3 == 0:
                    elif parm2 == exec_flags_abort:
                        Decomp = "IfAbort"
                        # if param3 != 0:
                    elif parm2 == exec_flags_exec_reboot:
                        Decomp = "IfRebootFlag"
                        # if param3 != 0:
                    elif parm2 == exec_flags_silent:
                        Decomp = "IfSilent"
                        # if param3 != 0:
                    Decomp = Decomp + " %s" % self.LL(parm0, parm1)
                    break
                if case(e.EW_SETFLAG):
                    parm1 = self.S_Int(parm1)
                    if parm0 == exec_flags_exec_error:
                        if parm1 == 0:
                            Decomp = "ClearErrors"
                        else:
                            Decomp = "SetErrors"
                            DecompComment += str(parm1)
                    elif parm0 == exec_flags_errlvl:
                        Decomp = "SetErrorLevel %i" % parm1
                    elif parm0 == exec_flags_exec_reboot:
                        Decomp = "SetRebootFlag %s" % self.E(parm1, "false true ")
                    elif parm0 == exec_flags_silent:
                        Decomp = "SetSilent %s" % self.E(parm1, "normal silent ")
                    elif parm0 == exec_flags_all_user_var:
                        Decomp = "SetShellVarContext %s" % self.E(parm1, "current all ")
                    elif parm0 == exec_flags_autoclose:
                        Decomp = "SetAutoClose %s" % self.E(parm1, "false true ")
                    elif parm0 == exec_flags_alter_reg_view:
                        # TODO: Do what the TODO from the original code is saying....
                        # TODO: Test this!
                        KEY_WOW64_64KEY = 0x100
                        if parm2 == 1:
                            detaillevel = "lastused"
                        elif parm1 == KEY_WOW64_64KEY:
                            detaillevel = "64"
                        else:
                            detaillevel = str(parm1)
                        Decomp = "SetRegView %s" % detaillevel
                    elif parm0 == exec_flags_status_update:
                        if parm2 == 1:
                            detaillevel = "lastused"
                            # if lastcmd == e.EW_CALL and param1==0
                            DecompComment += "maybe call func_x above is >InitPluginsDir<"
                        else:
                            detaillevel = self.E(parm1 >> 1, "both textonly listonly none")
                        Decomp = "SetDetailsPrint %s" % detaillevel
                    else:
                        Decomp = "SetAutoClose,RebootFlag..."
                    break
                if case(e.EW_IFFLAG):
                    if parm2 == exec_flags_exec_error:
                        Decomp = "IfErrors"
                        # if param3 == 0:
                    elif parm2 == exec_flags_abort:
                        Decomp = "IfAbort"
                        # if param3 != 0:
                    elif parm2 == exec_flags_exec_reboot:
                        Decomp = "IfRebootFlag"
                        # if param3 != 0:
                    elif parm2 == exec_flags_silent:
                        Decomp = "IfSilent"
                        # if param3 != 0:
                    Decomp = Decomp + " %s %s" % self.LL(parm0, parm1)
                    break
                if case(e.EW_CREATEFONT):
                    Decomp = "CreateFont %s %s %s %s %s" % (
                        self.V(parm0),
                        self.Sq(parm1),
                        self.S(parm2),
                        self.S(parm3),
                        BitOptions(parm4, " /ITALIC /UNDERLINE /STRIKE"),
                    )
                    break
                if case(e.EW_SENDMESSAGE):
                    # TODO: Pack WM_MSGs inside some init
                    WM_MSGs = {}
                    import win32con

                    for (k, v) in win32con.__dict__.items():
                        if k.startswith("WM_"):
                            WM_MSGs[v] = k

                    HWND = self.S(parm1)
                    msg = self.S(parm2)
                    msgAsText = WM_MSGs.get(eval(msg))

                    paramflag = parm5 & 3
                    if paramflag == 1:
                        wparam = self.S(parm3, "STR:")
                    else:
                        wparam = self.S(parm3)

                    if paramflag == 2:
                        lparam = self.S(parm4, "STR:")
                    else:
                        lparam = self.S(parm4)

                    TimeOut = self.II(parm5 >> 2, "/TIMEOUT=", True)

                    user_var = "" if parm0 < 0 else self.V(parm0)

                    Decomp = "SendMessage %s %s/*$(%s)*/ %s %s %s %s" % (
                        HWND,
                        msg,
                        msgAsText,
                        wparam,
                        lparam,
                        user_var,
                        TimeOut,
                    )

                    break
                if case(e.EW_MESSAGEBOX):
                    MB_IDs = " IDOK IDCANCEL IDABORT IDRETRY IDIGNORE IDYES IDNO"
                    # MB_IDsBitWidth = 3 # from 0..7 that be b000 to b111 -> 3bit's
                    MB_IDsBitMask = 7

                    BitsPerHexDigit = 4
                    installerIsSilentBitPos = (5 * BitsPerHexDigit) + 1
                    installerIsSilent = parm0 >> installerIsSilentBitPos
                    SD_option = "/SD %s" % self.E(installerIsSilent, MB_IDs) if installerIsSilent else ""
                    parm0 &= ~(MB_IDsBitMask << installerIsSilentBitPos)

                    MB = self.MB_Style(parm0)

                    MB_Text = self.Sq(parm1)
                    Decomp = "MessageBox  %s %s %s %s %s %s %s" % (
                        MB,
                        MB_Text,
                        SD_option,
                        self.E(parm2, MB_IDs),
                        self.J(parm3),
                        self.E(parm4, MB_IDs),
                        self.J(parm5),
                    )

                    if MB_Text == "Error! Can't initialize plug-ins directory. Please try again later.":
                        DecompComment += 'Name of this function is "Initialize_____Plugins" - Plz delete it and replace all Calls (+SetDetailsPrint lastused) with "InitPluginsDir"'

                    # uninstall_mode?
                    #   Initialize_____Plugins
                    # un.Initialize_____Plugins

                    break
                if case(e.EW_FINDWINDOW):
                    Decomp = "FindWindow %s %s %s %s %s" % (
                        self.V(parm0),
                        self.Sq(parm1),
                        self.Sq(parm2),
                        self.Sq(parm3),
                        self.S(parm4),
                    )
                    break
                if case(e.EW_REGISTERDLL):

                    # \nsis-2.09-src\Source\lang.h
                    # NLF_REGISTERING = -62
                    # NLF_UNREGISTERING = -61 ?

                    dllfile = self.S(parm0)
                    function_name = self.S(parm1)
                    nlf = self.II(parm2)

                    NOUNLOAD = "/NOUNLOAD" if parm3 == 1 else ""

                    if function_name == "DllUnregisterServer":
                        # nlf == NLF_UNREGISTERING
                        Decomp = "UnRegDLL  %s" % dllfile

                    elif function_name == "DllRegisterServer":
                        # nlf == NLF_REGISTERING
                        Decomp = "RegDLL  %s" % dllfile

                    else:
                        # nlf == 0
                        Decomp = "CallInstDLL  %s %s %s" % (dllfile, NOUNLOAD, function_name)

                    DecompComment = "maybe that from TOK__PLUGINCOMMAND sequence: EW_REGISTERDLL <- EW_PUSHPOP <- EW_UPDATETEXT <- EW_EXTRACTFILE <-EW_CALL"
                    DecompComment += (
                        '# or sth like >InstallOptions::initDialog "$INI"< CallInstDLL InstallOptions.dll  Push $INI SetDetailsPrint lastused File Call $PLUGINSDIR'
                        if parm4
                        else ""
                    )

                    # function_name: %s |     function_name ,
                    DecompComment += "#nfl: %s | DoNot_FreeLibrary: %s | Do_GetModuleHandle: %s" % (
                        nlf,
                        self.II(parm3),
                        self.II(parm4),
                    )

                    break
                if case(e.EW_COPYFILES):
                    FOF_SILENT = 4
                    FOF_NOCONFIRMATION = 0x10
                    FOF_FILESONLY = 0x80
                    FOF_SIMPLEPROGRESS = 0x100
                    FOF_NOCONFIRMMKDIR = 0x200

                    flags = ""
                    # parm4 = int( S(parm4) )
                    if parm4 and FOF_FILESONLY:  # and not(parm2 and FOF_SIMPLEPROGRESS)
                        flags += " /FILESONLY"
                    if parm4 and FOF_SILENT:
                        flags += " /SILENT"

                    # TODO: Re-enable this once I know how
                    # DecompComment = "%s %s" % (self.S(parm2), self.S(parm3))
                    Decomp = "CopyFiles %s %s %s" % (flags, self.S(parm0), self.S(parm1))
                    break
                if case(e.EW_SETFILEATTRIBUTES):
                    FILE_ATTRIBUTE_READONLY = 0x0001
                    FILE_ATTRIBUTE_HIDDEN = 0x0002
                    FILE_ATTRIBUTE_SYSTEM = 0x0004
                    FILE_ATTRIBUTE_ARCHIVE = 0x0020
                    FILE_ATTRIBUTE_NORMAL = 0x0080
                    FILE_ATTRIBUTE_TEMPORARY = 0x0100
                    FILE_ATTRIBUTE_OFFLINE = 0x1000

                    FILE_ATTRIBUTES = {
                        FILE_ATTRIBUTE_NORMAL: "NORMAL",
                        FILE_ATTRIBUTE_ARCHIVE: "ARCHIVE",
                        FILE_ATTRIBUTE_HIDDEN: "HIDDEN",
                        FILE_ATTRIBUTE_OFFLINE: "OFFLINE",
                        FILE_ATTRIBUTE_READONLY: "READONLY",
                        FILE_ATTRIBUTE_SYSTEM: "SYSTEM",
                        FILE_ATTRIBUTE_TEMPORARY: "TEMPORARY",
                        FILE_ATTRIBUTE_NORMAL: "0",
                    }
                    RawAttributes = parm1
                    StrAttributes = BitOptions(RawAttributes, FILE_ATTRIBUTES, "|")

                    Decomp = "SetFileAttributes %s %s" % (self.S(parm0), StrAttributes)
                    break
                if case(e.EW_RENAME):
                    Decomp = "Rename %s %s %s" % (
                        "/REBOOTOK" if parm2 else "",
                        self.S(parm0),
                        self.S(parm1),
                    )
                    break
                if case(e.EW_RMDIR):
                    # define DEL_DIR 1
                    # define DEL_RECURSE 2
                    # define DEL_REBOOT 4
                    # define DEL_SIMPLE 8
                    Decomp = "RMDir %s %s" % (self.S(parm0), BitOptions(parm1, " /r /REBOOTOK"))
                    break
                if case(e.EW_DELETEFILE):

                    Decomp = "Delete %s %s" % (
                        "/REBOOTOK" if parm1 else "",
                        self.S(parm0),
                    )
                    break
                if case(e.EW_EXECUTE):
                    if parm2:
                        Decomp = "ExecWait %s %s" % (self.S(parm0), self.V(parm1))
                    else:
                        Decomp = "Exec %s" % self.S(parm0)

                    break
                if case(e.EW_SHELLEXEC):
                    Decomp = "ExecShell %s %s %s %s" % (
                        self.S(parm0),
                        self.S(parm1),
                        self.S(parm2),
                        self.E(
                            parm3,
                            "SW_SHOWDEFAULT  SW_SHOWMAXIMIZED SW_SHOWMINIMIZED SW_HIDE SW_SHOW SW_SHOWNA SW_SHOWMINNOACTIVE",
                        ),
                    )  # no SW_SHOWNORMAL
                    DecompComment = self.S(parm5)
                    break
                if case(e.EW_EXTRACTFILE):

                    SetOverwrite = parm0 & 7

                    MB_Const = parm0 >> 3

                    IDCANCEL = 2
                    isIDCANCEL = MB_Const & (IDCANCEL << 21)
                    MB_Const &= ~(IDCANCEL << 21)
                    if isIDCANCEL:
                        MB_Const |= IDCANCEL

                    SetOverwriteAsText = self.E(SetOverwrite, "on off try ifnewer ifdiff lastused")
                    if self.cls_Decomp.SetOverwrite != SetOverwrite:
                        Decomp = "SetOverwrite " + SetOverwriteAsText + "\n" + instident

                    try:
                        dt = ""
                        # Int32x32To64

                        ft_dec = struct.unpack(">Q", struct.pack(">ll", parm4, parm3))[0]

                        from datetime import datetime

                        # UnixTimeToFileTime http://support.microsoft.com/kb/167296
                        EPOCH_AS_FILETIME = 116444736000000000
                        HUNDREDS_OF_NANOSECONDS = 10000000

                        # Don't use Timezone Information - timpstamp was get (during compiling) via GetFileTime()
                        dt = datetime.fromtimestamp((ft_dec - EPOCH_AS_FILETIME) / HUNDREDS_OF_NANOSECONDS)
                    except Exception:
                        pass

                    ##ifdef _WIN32
                    # FILETIME ft;
                    # if (GetFileTime(hFile,NULL,NULL,&ft))
                    # {
                    # PULONGLONG fti = (PULONGLONG) &ft;
                    # *fti -= *fti % 20000000; // FAT write time has a resolution of 2 seconds
                    # ent.offsets[3]=ft.dwLowDateTime, ent.offsets[4]=ft.dwHighDateTime;
                    # }
                    ##else

                    # ll = Int32x32To64(t, 10000000) + 116444736000000000;
                    #
                    # struct stat st;
                    # if (!fstat(fd, &st))
                    # {
                    # unsigned long long ll = (st.st_mtime * 10000000LL) + 116444736000000000LL;
                    # ll -= ll % 20000000; // FAT write time has a resolution of 2 seconds
                    # ent.offsets[3] = (int) ll, ent.offsets[4] = (int) (ll >> 32);
                    # }
                    ##endif

                    FileName = self.Sq(parm1)
                    FileOffset = parm2

                    Decomp += (
                        "File  %s "
                        "%s   data_handle/Offset: %s  SetOverwrite %s  MB_Const:%x - %s  Time:%s (%X %X) msg:%s"
                        % (
                            FileName,
                            NSIS_COMMENT,
                            self.B(FileOffset),
                            SetOverwriteAsText,
                            MB_Const,
                            self.MB_Style(MB_Const),
                            dt,
                            parm3,
                            parm4,
                            self.S(parm5),
                        )
                    )
                    self.cls_Decomp.SetOverwrite = SetOverwrite

                    self.FileExtract.Files.append((FileName, self.FileExtract.CurDir, FileOffset, ft_dec))

                    DecompComment = (
                        "Optimisation hint: >> File FOO.DIR\\%s<<  => IF prev cmd is 'SetOutPath' followed by a single(!) 'File' command(...followed by SetOutPath somewhere later)"
                        % FileName
                    )

                    break
                if case(e.EW_SHOWWINDOW):
                    if parm3 == 1:
                        Decomp = "EnableWindow %s %s " % (self.S(parm0), self.S(parm1))
                    elif parm2 == 1:
                        Decomp = "HideWindow"
                        DecompComment = "TOK_HIDEWINDOW %s %s" % (self.S(parm0), self.S(parm1))
                    else:
                        # handle = self.S(parm0)
                        showState = self.S(parm1)
                        Decomp = "ShowWindow %s %s " % (self.S(parm0), self.S(parm1))

                        if showState == "5":  # and (handle=='$HWNDPARENT'):
                            # Skipping validation of the next entry
                            break

                            # skip next
                            # i+=1
                            n_which = fo.uInt32()
                            # n_parm0 = fo.Int32()
                            # n_parm1 = fo.Int32()
                            # n_parm2 = fo.Int32()
                            # n_parm3 = fo.Int32()
                            # n_parm4 = fo.Int32()
                            # n_parm5 = fo.Int32()

                            fo.seek(-4, os.SEEK_CUR)
                            if e.EW_BRINGTOFRONT != n_which:
                                print("ERROR !!! Expected next command to be EW_BRINGTOFRONT")
                                # i-=1
                                # fo.seek (-4*7,os.SEEK_CUR)
                            else:
                                skipCommand = True

                            # Decomp = "BringToFront"

                    break
                if case(e.EW_SECTIONSET):
                    # SECTION_FIELD_GET_name_ptr = 0
                    # SECTION_FIELD_SET_name_ptr = -1

                    what = ""
                    Arg2 = '""'
                    # default = parm3

                    if parm2 in (0, ~0):
                        what = "Text"
                        Arg2 = self.Sq(parm4)
                    if parm2 in (1, ~1):
                        what = "InstTypes"
                        Arg2 = self.Sq(parm1)
                    if parm2 in (2, ~2):
                        what = "Flags"
                        Arg2 = self.Sq(parm1)  # ; assert(default == 1)
                    if parm2 in (5, ~5):
                        what = "Size"
                        Arg2 = self.Sq(parm1)

                    if parm2 >= 0:
                        Decomp = "SectionGet%s %s %s" % (what, self.SECTION_FIELD(parm0), self.V(parm1))
                    else:
                        Decomp = "SectionSet%s %s %s" % (what, self.SECTION_FIELD(parm0), Arg2)

                    break
                if case(e.EW_INSTTYPESET):

                    if parm3 == 0:
                        if parm2 == 0:
                            Decomp = "InstTypeGetText %s %s" % (self.S(parm0), self.V(parm1))
                        elif parm2 == 1:
                            Decomp = "InstTypeSetText %s %s" % (self.S(parm0), self.Sq(parm1))

                    elif parm3 == 1:
                        if parm2 == 1:
                            Decomp = "SetCurInstType %s" % (self.S(parm0))
                        elif parm2 == 0:
                            Decomp = "GetCurInstType %s" % (self.V(parm1))
                    break

                try:
                    if DEBUG:
                        print("   parm0: %s" % self.S(parm0))
                        print("   parm1: %s" % self.S(parm1))
                        print("   parm2: %s" % self.S(parm2))
                        print("   parm3: %s" % self.S(parm3))
                        print("   parm4: %s" % self.S(parm4))
                        print("   parm5: %s" % self.S(parm5))
                    Decomp = "Decompiling that command is not implemented yet!"
                    DecompComment = lineRawInfo
                except Exception:
                    pass
                #           stop()
                break

            # SectionTxt = self.MakeSectionTxt(self.Tokenindex)

            DecompComment = ("\t\t; " if DecompComment else "") + DecompComment

            DoSupress = not self.cls_Decomp.isInsideSection and self.supressCodeOutsideSections
            if DoSupress:
                Decomp = "SUPRESSED!!!  " + Decomp

            if skipCommand:
                Decomp = "SKIPPED!!!  " + Decomp

            if DEBUG and i in self.cls_Decomp.Functions:
                print(self.cls_Decomp.Functions[i])

            if DEBUG and i in self.cls_Decomp.Labels:
                print(self.cls_Decomp.Labels[i])

            lineDecomp = instident + "%s" % (Decomp)
            lineDecompcmt = instident + "// %s" % (DecompComment)

            if DEBUG:
                # print(SectionTxt)
                print(lineDecomp)
            # print(lineDecompcmt)

            #        if SectionTxt:
            #            cls_Decomp.SectionTxt[i] = SectionTxt

            if not (skipCommand):
                self.cls_Decomp.Tokens[i] = lineRawInfo
                self.cls_Decomp.Decomps[i] = Decomp
                self.cls_Decomp.Comments[i] = DecompComment
            self.cls_Decomp.DoSupress[i] = DoSupress or skipCommand

        self.decompFile.append("\n; --------------------")
        self.decompFile.append("; ENTRIES\n")
        self.SaveDecompiledToNsiFile()

    def MakeSectionTxt(self, Tokenindex):
        SectionTxt = ""
        pos = Tokenindex - TOKENBASE

        if pos in self.cls_Decomp.Sections_end:
            SectionTxt += self.cls_Decomp.Sections_end[pos] + ""
            self.cls_Decomp.isInsideSection = False

        if pos in self.cls_Decomp.Sections_start:
            if self.cls_Decomp.isInsideFunction:
                self.decompFile.append("FunctionEnd\n")
                self.cls_Decomp.isInsideFunction = False

            SectionTxt += (
                self.cls_Decomp.Sections_start[pos]
                + " "
                + self.cls_Decomp.Sections_idx.get(pos, "")
                + ""
                + self.cls_Decomp.SectionsIN.get(pos, "")
                + ""
            )
            self.cls_Decomp.isInsideSection = True

        if pos in self.cls_Decomp.Functions:
            self.cls_Decomp.isInsideSection |= not ("FunctionEnd" in self.cls_Decomp.Functions[pos])

        return SectionTxt  # , isInsideSection

    def SaveDecompiledToNsiFile(self):
        # write nsi files (second pass)
        # Now also post defined labels are written.
        for i in range(TOKENBASE, self.Tokenindex):
            # Write SectionTxt 'Section[Group]...', 'SectionIn...', 'Section[Group] End'
            SectionTxt = self.MakeSectionTxt(i)
            if SectionTxt:
                self.decompFile.append(SectionTxt)

            # Write Function
            if i in self.cls_Decomp.Functions:
                if self.cls_Decomp.isInsideFunction:
                    self.decompFile.append("FunctionEnd\n")
                    # self.cls_Decomp.isInsideFunction = False
                else:
                    self.cls_Decomp.isInsideFunction = True

                self.decompFile.append("%s" % self.cls_Decomp.Functions[i])

            # Write Labels
            if i in self.cls_Decomp.Labels:
                self.decompFile.append("%s" % self.cls_Decomp.Labels[i])

            if self.cls_Decomp.DoSupress.get(i, False) is False:
                if self.supressRawTokens is False:
                    # Write Token info
                    self.decompFile.append(instident + instident + "%s" % self.cls_Decomp.Tokens.get(i))
                # Write Decompiled Lines
                self.decompFile.append(
                    instident + "%s%s" % (self.cls_Decomp.Decomps.get(i), self.cls_Decomp.Comments.get(i))
                )

        if self.cls_Decomp.isInsideFunction:
            self.decompFile.append("FunctionEnd\n")

    def generate_setup_file(self):
        self.decompFile.append("; --------------------")
        self.decompFile.append("; HEADER\n")

        if self.S(self.nsis.header.install_directory_auto_append):
            DecompLine = "Name %s" % self.S(self.nsis.header.install_directory_auto_append)
            self.decompFile.append(DecompLine)
            DecompLine = "OutFile %s ; NsiDecompiler: generated value!" % self.S(
                self.nsis.header.install_directory_auto_append, "", ".exe"
            )
            self.decompFile.append(DecompLine)

        def flip_rgb(value):
            return struct.unpack(">I", struct.pack("<I", value))[0] >> 8

        # Fix because the original nrs library extract them as <I, we need to flip endianness and shift 8
        bg_color1s = flip_rgb(self.nsis.header.bg_color1s)
        bg_color2 = flip_rgb(self.nsis.header.bg_color2)
        bg_textcolor = flip_rgb(self.nsis.header.bg_textcolor)
        lb_fg = flip_rgb(self.nsis.header.lb_fg)
        lb_bg = flip_rgb(self.nsis.header.lb_bg)

        EMPTYCOLOR = 0xFFFFFF
        if not (bg_color1s == bg_color2 == bg_textcolor == EMPTYCOLOR):
            BGGradient = "BGGradient %.6X %.6X %.6X" % (
                bg_color1s,
                bg_color2,
                bg_textcolor,
            )
            self.decompFile.append(BGGradient)

        if not (lb_fg == lb_bg == EMPTYCOLOR):
            InstallColors = "InstallColors %.6X %.6X" % (lb_fg, lb_bg)
            self.decompFile.append(InstallColors)

        if self.nsis.header.install_directory_ptr:
            DecompLine = "InstallDir %s" % self.S(self.nsis.header.install_directory_ptr)
            self.decompFile.append(DecompLine)

        if self.S(self.nsis.header.install_reg_key_ptr):
            DecompLine = "InstallDirRegKey %s %s %s" % (
                self.E(self.nsis.header.install_reg_rootkey & 0xF, REG_HKEYS),
                self.S(self.nsis.header.install_reg_key_ptr),
                self.S(self.nsis.header.install_reg_value_ptr),
            )
            self.decompFile.append(DecompLine)

        # Just some static lines to Quickfix certain compiling issues like AddBrandingImage
        self.decompFile.append(HeaderAddlines)

        if self.nsis.header.unicode:
            self.decompFile.append("Unicode true")

        for f in self.nsis.header._fields:
            if f.startswith("code_"):
                attribute = self.nsis.header.__getattribute__(f)
                if attribute != -1:
                    self.ns_func(f[5:], ".", attribute + TOKENBASE, False)

        # dump Install Types
        for item in self.DumpInstTypes():
            line = "InstType %s" % item
            self.decompFile.append(line)

        self.decompFile.append("\n; --------------------")
        self.decompFile.append("; PAGES\n")

        self.dumpPages()

        self.decompFile.append("\n; --------------------")
        self.decompFile.append("; SECTIONS\n")

        self.dumpSections()

        self.decompFile.append("\n; --------------------")
        self.decompFile.append("; VARIABLES\n")

        self.ProcessEntries()
        
    def save_setup_file(self, path="output"):
        with open(path, "w") as f:
            for line in self.decompFile:
                f.write(f"{line}\n")
                
    @staticmethod
    def from_path(path):
        return Extractor(NSIS.from_path(path))
        
        

# Possible tests:
# c2a13d7d4d2ca6bef8ebdb914943563a1b583d03cf093f03fc3ac5e9cb9e5485
#   -> 4f7421fc4a57db0c6d5929f0d8fcbcf70b3d90bc9248399bb6cb9c647f98c013
# 1670d4948cd7354ce8b2b77bde241dc0cdb8920d4ff0a64209c0bfe943aad8da
#   -> 32ababd3650770372bebda92d2d7014b7fd699b31f9f3c4fd83e529b4ece5a38
# 291df8186e62df74b8fcf2c361c6913b9b73e3e864dde58eb63d5c3159a4c32d
#   -> c544b90fd61190994d7ced343c05cd755a96653648daed03d541bf0a815f08d5


if __name__ == '__main__':
    nsis_target = sys.argv[1]
    extractor = Extractor.from_path(nsis_target)
    extractor.generate_setup_file()
    extractor.save_setup_file()
