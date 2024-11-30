import json
from django.http import JsonResponse
from .models import Donation, BotUser

def yookassa_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        if data['event'] == 'payment.succeeded':
            payment_id = data['data']['id']
            donor_id = data['data']['metadata']['donor_id']
            speaker_id = data['data']['metadata']['speaker_id']
            amount = data['data']['amount']['value']

            donor = BotUser.objects.get(telegram_id=donor_id)
            speaker = BotUser.objects.get(telegram_id=speaker_id)

            Donation.objects.create(
                donor=donor,
                speaker=speaker,
                amount=amount,
            )

            return JsonResponse({'status': 'success'}, status=200)

    return JsonResponse({'status': 'error'}, status=400)
