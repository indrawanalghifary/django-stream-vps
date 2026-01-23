from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, CommentEvent, GiftEvent, FollowEvent, ShareEvent, LikeEvent
import asyncio
# Create the client
client: TikTokLiveClient = TikTokLiveClient(unique_id="@geminiparfumm")


# # Listen to an event with a decorator!
# @client.on(ConnectEvent)
# async def on_connect(event: ConnectEvent):
#     print(f"Connected to @{event.unique_id} (Room ID: {client.room_id}")
#     # hasil = await client.web.fetch_room_info(client.room_id)
#     # print(hasil)
    

# # Or, add it manually via "client.add_listener()"
# async def on_comment(event: CommentEvent) -> None:
#     print(f"{event.user.nickname} -> {event.comment}")


# async def on_gift(event: GiftEvent) -> None:
#     print(f"{event.user.nickname} sent {event.gift.name} x{event.gift.repeat_count}")

# async def on_follow(event: FollowEvent) -> None:
#     print(f"{event.user.nickname} just followed!")

# async def on_share(event: ShareEvent) -> None:
#     print(f"{event.user.nickname} just shared the livestream!")

# async def on_like(event: LikeEvent) -> None:
#     print(f"{event.user.nickname} just liked the livestream!")

# client.add_listener(CommentEvent, on_comment)
# client.add_listener(GiftEvent, on_gift)
# client.add_listener(FollowEvent, on_follow)
# client.add_listener(ShareEvent, on_share)
# client.add_listener(LikeEvent, on_like)

async def test():
    await client.start()
    room_info = await client.web.fetch_room_info(client.room_id)
    # with open("room_info.json", "w", encoding="utf-8") as f:
    #     import json
    #     json.dump(room_info, f, ensure_ascii=False, indent=4)
    # print(f'RTMF URL: {room_info.get("stream_url").get("rtmp_pull_url")}')
    print(room_info)
    

if __name__ == '__main__':
    # Run the client and block the main thread
    # await client.start() to run non-blocking

    asyncio.run(test())
    # client.run()
