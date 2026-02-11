import requests

BOT_TOKEN = "8521706280:AAHTgbWj-Zr6683jNZQVS6BBiu7KcZ_O6UY"

# Получить информацию о боте
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
response = requests.get(url)
print("Информация о боте:")
print(response.json())

# Получить последние обновления
url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
response = requests.get(url)
print("\nПоследние обновления (сообщения от пользователя):")
data = response.json()
if data.get('result'):
    for update in data['result']:
        print(f"\nUpdate ID: {update['update_id']}")
        if 'message' in update:
            msg = update['message']
            print(f"Chat ID: {msg['chat']['id']}")
            print(f"User ID: {msg['from']['id']}")
            print(f"Сообщение: {msg.get('text', 'No text')}")
else:
    print("Нет обновлений. Напишите боту сообщение в Telegram!")
