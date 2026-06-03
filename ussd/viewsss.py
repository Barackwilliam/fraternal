from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

@csrf_exempt
def ussd_callback(request):
    if request.method == 'POST':
        session_id = request.POST.get('sessionId')
        phone_number = request.POST.get('phoneNumber')
        text = request.POST.get('text', '')

        if text == '':
            response = "CON Karibu Shamba Mfukoni! 🌾\n"
            response += "1. Hali ya Hewa\n"
            response += "2. Bei za Soko\n"
            response += "3. Daktari wa Mazao\n"
            response += "0. Toka"

        elif text == '1':
            response = "END Hali ya Hewa leo:\n"
            response += "Dar es Salaam: Jua, 32°C\n"
            response += "Mvua inatarajiwa jioni"

        elif text == '2':
            response = "CON Bei za Soko leo:\n"
            response += "1. Mahindi\n"
            response += "2. Maharagwe\n"
            response += "3. Mpunga"

        elif text == '2*1':
            response = "END Bei ya Mahindi:\n"
            response += "Dar: TZS 800/kg\n"
            response += "Arusha: TZS 750/kg"

        elif text == '2*2':
            response = "END Bei ya Maharagwe:\n"
            response += "Dar: TZS 2,500/kg\n"
            response += "Arusha: TZS 2,200/kg"

        elif text == '2*3':
            response = "END Bei ya Mpunga:\n"
            response += "Dar: TZS 1,200/kg\n"
            response += "Arusha: TZS 1,100/kg"

        elif text == '3':
            response = "CON Daktari wa Mazao:\n"
            response += "1. Majani yanageuka njano\n"
            response += "2. Wadudu kwenye mmea\n"
            response += "3. Mmea kunyauka\n"
            response += "0. Rudi nyuma"

        elif text == '3*1':
            response = "END Tatizo: Majani njano\n"
            response += "Sababu: Upungufu wa Nitrogen\n"
            response += "Suluhisho: Weka mbolea ya Urea"

        elif text == '3*2':
            response = "END Tatizo: Wadudu\n"
            response += "Sababu: Aphids au Thrips\n"
            response += "Suluhisho: Nyunyizia dawa ya Lambda"

        elif text == '3*3':
            response = "END Tatizo: Mmea kunyauka\n"
            response += "Sababu: Ukosefu wa maji au ugonjwa wa mizizi\n"
            response += "Suluhisho: Mwagilia na angalia mizizi"

        elif text == '0':
            response = "END Asante kutumia Shamba Mfukoni!\n"
            response += "Shamba bora, maisha bora! 🌾"

        else:
            response = "END Samahani, chaguo hilo halipo."

        return HttpResponse(response, content_type='text/plain')

    # GET request — browser tu, si Africa's Talking
    return HttpResponse("Shamba Mfukoni USSD Service inafanya kazi! ✅", content_type='text/plain')