import json
from time import sleep
import asyncio
import requests
import requests.auth

from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub.exceptions import EventHubError
from azure.eventhub import EventData

CONNECTION_STR = "Endpoint=sb://oblaknamespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=BDV7M9DqVrubNvcQSLRoF2fgUVco3nf+B+AEhMZRX1s="
EVENTHUB_NAME = "cleanhub"


async def run():
    client_auth = requests.auth.HTTPBasicAuth(
        "paTgAbKTO4I2qfRzcJvckQ", "qv0fRkYDKY3XDRfmQOXl7TIeupGOnA"
    )
    post_data = {
        "grant_type": "password",
        "username": "oblak-faks-labos",
        "password": "severina123",
    }
    headers = {"User-Agent": "ChangeMeClient/0.1 by YourUsername"}

    # Get access token
    response = requests.post(
        "https://www.reddit.com/api/v1/access_token",
        auth=client_auth,
        data=post_data,
        headers=headers,
    )
    auth_resp = response.json()

    # Fetch data
    headers = {
        "Authorization": f"bearer {auth_resp['access_token']}",
        "User-Agent": "ChangeMeClient/0.1 by YourUsername",
    }

    after = ""
    for i in range(5):
        url = f"https://oauth.reddit.com/r/dataengineering/top/?limit=10&t=all&after={after}"
        response = requests.get(url, headers=headers)
        resp_json = response.json()

        after = resp_json["data"]["after"]

        producer = EventHubProducerClient.from_connection_string(
            conn_str=CONNECTION_STR, eventhub_name=EVENTHUB_NAME
        )

        async with producer:
            event_data_batch = await producer.create_batch()

            for post in resp_json["data"]["children"]:
                print(f"Adding {post['data']['title']} to batch")
                data = json.dumps(post)
                event_data_batch.add(EventData(data))

            print("Sending batch")
            await producer.send_batch(event_data_batch)

        print("sleeping")
        sleep(10)

    while True:
        sleep(3600)
        continue


print("HEJ;")
asyncio.run(run())

print("GOTOVO!")
