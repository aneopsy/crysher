import os, sys, base64

class bcolors:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERL = '\033[4m'
    ENDC = '\033[0m'
    backBlack = '\033[40m'
    backRed = '\033[41m'
    backGreen = '\033[42m'
    backYellow = '\033[43m'
    backBlue = '\033[44m'
    backMagenta = '\033[45m'
    backCyan = '\033[46m'
    backWhite = '\033[47m'

def start():
    print((" --- {0}Crysher v1.0 by AneoPsy{1} --- \n    {2}Crypter{1} & {2}Decrypter{1} tool.".format(bcolors.GREEN, bcolors.ENDC, bcolors.YELLOW)))
    print("1 > Crypter")
    print("2 > Decrypter")
    choix = input("> ")
    if int(choix) == 1:
        crypter()
    elif int(choix) == 2:
        decrypted()

def crypter():
    os.system("clear")
    print(("*** {0}Crypter{1} ***".format(bcolors.GREEN, bcolors.ENDC)))
    file = input("Filename > ")
    try:
        FileName = open(file, 'r')
        print(("[+]{0}File correct{1}".format(bcolors.GREEN, bcolors.ENDC)))
    except:
        print(("[-]{0}Wrong file selected{1}".format(bcolors.RED, bcolors.ENDC)))
        exit()
    print("[*]Cryptage ...")
    text = FileName.read()
    TextEncode = base64.b64encode(text.encode())
    TextEncode = TextEncode.decode()
    FileCrypted = open(file, 'w')
    FileCrypted.write(TextEncode)
    print(("[+]{0}File crypted{1}".format(bcolors.GREEN, bcolors.ENDC)))
    nameBackup = "backup." + file
    backup = open(nameBackup, 'w')
    backup.write(text)
    exit()

def decrypted():
    os.system("clear")
    print(("*** {0}Decrypter{1} ***".format(bcolors.GREEN, bcolors.ENDC)))
    file = input("Filename > ")
    try:
        FileName = open(file, 'r')
        print(("[+]{0}File correct{1}".format(bcolors.GREEN, bcolors.ENDC)))
    except:
        print(("[-]{0}Wrong file selected{1}".format(bcolors.RED, bcolors.ENDC)))
        exit()
    print("[*]Decryptage ...")
    text = FileName.read()
    TextDecode = base64.b64decode(text.encode())
    TextDecode = TextDecode.decode()
    FileDeCrypted = open(file, 'w')
    FileDeCrypted.write(TextDecode)
    print(("[+]{0}File decrypted{1}".format(bcolors.GREEN, bcolors.ENDC)))
    nameBackup = "backup." + file
    backup = open(nameBackup, 'w')
    backup.write(text)
    exit()

if __name__ == "__main__":
    try:
        start()
    except KeyboardInterrupt:
        print (("{0}Crypter{1} was interrupted...\n".format(bcolors.RED, bcolors.ENDC)))
    except:
        sys.exit()
