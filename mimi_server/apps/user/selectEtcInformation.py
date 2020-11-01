def selectChineseZodiac(year):
    if int(year)%12 == 0:
        return "원숭이"
    elif int(year)%12 == 1:
        return "닭"
    elif int(year)%12 == 2:
        return "개"
    elif int(year)%12 == 3:
        return "돼지"
    elif int(year)%12 == 4:
        return "쥐"
    elif int(year)%12 == 5:
        return "소"
    elif int(year)%12 == 6:
        return "범"
    elif int(year)%12 == 7:
        return "토끼"
    elif int(year)%12 == 8:
        return "용"
    elif int(year)%12 == 9:
        return "뱀"
    elif int(year)%12 == 10:
        return "말"
    elif int(year)%12 == 11:
        return "양"
    
def selectStar(month, date) :
    if int(month) == 1:
        if int(date)>=20:
            return "물병자리"
        else:
            return "염소자리"
    elif int(month) == 2:
        if int(date)>=19:
            return "물고기자리"
        else:
            return "물병자리"
    elif int(month) == 3:
        if int(date)>=21:
            return "양자리"
        else:
            return "물고기자리"
    elif int(month) == 4:
        if int(date)>=20:
            return "황소자리"
        else:
            return "양자리"
    elif int(month) == 5:
        if int(date)>=21:
            return "쌍둥이자리"
        else:
            return "황소자리"
    elif int(month) == 6:
        if int(date)>=22:
            return "게자리"
        else:
            return "쌍둥이자리"
    elif int(month) == 7:
        if int(date)>=23:
            return "사자자리"
        else:
            return "게자리"
    elif int(month) == 8:
        if int(date)>=23:
            return "처녀자리"
        else:
            return "사자자리"
    elif int(month) == 9:
        if int(date)>=24:
            return "천칭자리"
        else:
            return "처녀자리"
    elif int(month) == 10:
        if int(date)>=23:
            return "전갈자리"
        else:
            return "천칭자리"
    elif int(month) == 11:
        if int(date)>=23:
            return "사수자리"
        else:
            return "전갈자리"
    elif int(month) == 12:
        if int(date)>=25:
            return "염소자리"
        else:
            return "사수자리"
        