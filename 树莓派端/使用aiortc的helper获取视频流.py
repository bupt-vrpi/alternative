import asyncio
import json

from aiohttp import ClientSession, WSMsgType
from aiortc import RTCPeerConnection
from aiortc.contrib.media import MediaPlayer
from aiortc.contrib.signaling import object_from_string, object_to_string

options = {"video_size": "720*720", "framerate": "12"}


async def run(pc):
    session = ClientSession()

    async with session.ws_connect("ws://39.102.116.49:8080") as ws:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                data = json.loads(msg.data)

                if data["type"] == "offerOrAnswer":
                    await pc.setRemoteDescription(
                        object_from_string(json.dumps(data["msg"]))
                    )

                    if data["msg"]["type"] == "offer":
                        pc.addTrack(
                            MediaPlayer(
                                "/dev/video0", format="v4l2", options=options
                            ).video
                        )
                        await pc.setLocalDescription(await pc.createAnswer())
                        await ws.send_str(
                            json.dumps(
                                {
                                    "type": "offerOrAnswer",
                                    "msg": json.loads(
                                        object_to_string(pc.localDescription)
                                    ),
                                }
                            )
                        )
                elif data["type"] == "candidate":
                    try:
                        await pc.addIceCandidate(
                            object_from_string(json.dumps(data["msg"]))
                        )
                    except:
                        pass


if __name__ == "__main__":
    pc = RTCPeerConnection()

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            run(
                pc=pc,
            )
        )
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(pc.close())
