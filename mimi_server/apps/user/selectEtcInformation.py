from django.db.models import Q
from mimi_server.apps.etcInformation.models import ChineseZodiac, Star

def selectChineseZodiac(year):
    return ChineseZodiac.objects.get(Q(order=int(year)%12))
    
def selectStar(month, date) :
    star = Star.objects.raw("SELECT name, start_date, end_date FROM \"etcInformation_star\" WHERE TO_DATE('"+ month + "-" + date + "', 'MM-DD') BETWEEN TO_DATE(start_date, 'MM-DD') AND TO_DATE(end_date, 'MM-DD')")
    
    if len(star) == 0 :
        return Star.objects.get(Q(name='염소자리'))
    return star[0]