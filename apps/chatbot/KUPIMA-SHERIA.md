# Kupima sheria za mazungumzo

Baada ya kubadilisha sheria, zipime kabla ya kuziacha kwa wateja.

## Jinsi ya kupima

```bash
python manage.py shell
```

```python
from apps.chatbot.models import BotConfig
from apps.chatbot.ai_engine import BotAIEngine

bot = BotConfig.objects.get(business_name='JamiiTek')   # au bot yoyote
print(bot.build_system_prompt())                        # angalia sheria zipo
```

Kisha fungua mazungumzo mapya kwenye WhatsApp na upitie majaribio haya.

## Majaribio sita

Kila moja linalenga tabia moja iliyoonekana kwenye mazungumzo ya
Mbossai Farm.

| # | Andika hivi | Kinachotakiwa | Kilichokuwa kikitokea |
|---|---|---|---|
| 1 | "Nataka website" kisha "Bei?" kisha "Bei ni ngapi?" | Bei itajwe **mara moja**. Ukiuliza tena, apate namba moja au swali linalomsaidia kubaini | Ilirudiwa "185,000 hadi 1,500,000" kila ujumbe |
| 2 | "Ndiyo" | Mstari mmoja au miwili | Aya tatu na orodha ya bold |
| 3 | Ujumbe wowote | Usimalizike kwa "Je, ungependa...?" kila mara | Kila ujumbe ulimalizika kwa swali |
| 4 | Endelea mazungumzo mistari mitano | Jina lako litajwe mwanzoni na mwishoni pekee | "Benon" kwenye kila ujumbe |
| 5 | "Itachukua muda gani?" | Aseme timu itakupa muda kwenye pendekezo | Aliahidi "siku 5 hadi 7" |
| 6 | "Sawa, tuanze" | Aseme **kitakachofanyika**, si kwamba kimeshafanyika | "Tayari nimeunganisha na timu yetu" — hakuwa amefanya |

## Kama bado inarudia

Angalia `max_context_msgs` kwenye usanidi wa bot. Ikiwa ndogo mno, bot
haioni ujumbe wa mwanzo wa mazungumzo, kwa hiyo haijui kwamba tayari
imeitaja bei. Namba nzuri ni **10 hadi 15**.

## Halijoto (temperature)

`ai_temperature` ya juu inaleta majibu yenye mabadiliko zaidi; ya chini
inaleta majibu yanayofanana. Kwa mazungumzo ya mauzo, **0.6 hadi 0.8**
inafaa. Chini ya 0.5 inaanza kusikika kama fomu.
