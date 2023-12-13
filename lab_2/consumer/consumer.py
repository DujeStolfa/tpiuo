import os
import json
from datetime import datetime

import asyncio
from azure.storage.filedatalake import DataLakeServiceClient

from azure.identity import DefaultAzureCredential
from azure.eventhub.aio import EventHubConsumerClient

EVENT_HUB_CONNECTION_STR = "Endpoint=sb://oblaknamespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=BDV7M9DqVrubNvcQSLRoF2fgUVco3nf+B+AEhMZRX1s="
EVENT_HUB_NAME = "cleanhub"
SAS_TOKEN = "KhFURePi7mXz6N/O8lKo8bCokyqH0b8wvRtVroet6QAetYOcJ6R8YgKlGVWaBPHzOOJ7tAPSVyfb+AStYmVwjQ=="
CONTAINER_NAME = "datacontainer"


async def on_event(partition_context, event):
    account_url = f"https://oblakstorage.dfs.core.windows.net"
    service_client = DataLakeServiceClient(account_url, credential=SAS_TOKEN)
    file_system_client = service_client.get_file_system_client(
        file_system=CONTAINER_NAME
    )

    objava = json.loads(event.body_as_str(encoding="UTF-8"))

    # Stvori folder
    dt = datetime.utcfromtimestamp(objava["data"]["created_utc"])
    new_dir = dt.strftime("%Y/%m/%d/%H/%M")
    directory_client = file_system_client.create_directory(new_dir)

    # Uploadaj podatke
    file_client = directory_client.get_file_client(f"{objava['data']['name']}.json")
    file_client.upload_data(str(objava["data"]), overwrite=True)

    # Log
    print(f"Uploaded {objava['data']['title']} to {new_dir}")

    await partition_context.update_checkpoint(event)


async def main():
    client = EventHubConsumerClient.from_connection_string(
        EVENT_HUB_CONNECTION_STR,
        consumer_group="$Default",
        eventhub_name=EVENT_HUB_NAME,
    )
    async with client:
        await client.receive(on_event=on_event, starting_position="@latest")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    print("START APP;")
    loop.run_until_complete(main())
    print("STOP APP!")
