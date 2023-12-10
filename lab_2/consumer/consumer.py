import asyncio

from azure.eventhub.aio import EventHubConsumerClient

EVENT_HUB_CONNECTION_STR = "Endpoint=sb://mostovi.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=ukCi1jQV55q6TksBn9/gwYtOFSzCdu3MV+AEhNDXLX8="
EVENT_HUB_NAME = "mostovi-hub"


async def on_event(partition_context, event):
    print(
        'Received the event: "{}" from the partition with ID: "{}"'.format(
            event.body_as_str(encoding="UTF-8"), partition_context.partition_id
        )
    )

    await partition_context.update_checkpoint(event)


async def main():
    client = EventHubConsumerClient.from_connection_string(
        EVENT_HUB_CONNECTION_STR,
        consumer_group="$Default",
        eventhub_name=EVENT_HUB_NAME,
    )
    async with client:
        await client.receive(on_event=on_event, starting_position="-1")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    print("START APP")
    loop.run_until_complete(main())
    print("STOP APP.")
