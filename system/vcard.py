import locale
def parse(raw):
    encoding = locale.getdefaultlocale()[1]
    raw=raw.decode(encoding)
    phones=0
    card={}
    card["phone"]={}
    phonetypes = {"CELL" : "Mobil", "HOME" : "Privat", "WORK" : "Dienstlich"}
    for line in raw.split("\r\n"):
        p=line.split(":")
        if line[:2]=="FN":
            card["name"]=p[1]
            
        if line[:1]=="N":
            n=p[1].split(";")
            try:
                card["first_name"]=n[1]
            except:
                card["first_name"]=""
            try:
                card["surname"]=n[0]
            except:
                card["surname"]=""
            
        if line[:3]=="UID":
            card["uid"]=p[1]
        
        if line[:3]=="TEL":
            try:
                t=p[0].split(";")
                typ=t[1].replace("TYPE=","")
                if typ!="FAX":
                    card["phone"][phones]={}
                    card["phone"][phones]["type"]=phonetypes[typ]
                    card["phone"][phones]["number"]=p[1].replace(" ","")
                    phones+=1
            except:
                pass
    
    return card