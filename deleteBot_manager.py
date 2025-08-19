import os
names = ['version.json','Infos.json','Speak.json','SpeakD.json','Users.json','owner.txt','BotMe.pyrubi']
for name in names:
    isok = os.path.isfile(name)
    if isok:os.remove(name)
print('deleted.')