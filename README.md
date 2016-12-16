# :clap: Pimaas

Pimass (pi-media as a service) is a tiny media player for raspberry pi exclusively controlled through an API. It runs in a full-screen kiosk mode, using framebuffer, and it accepts streaming requests. 


## Installation

1. Install the following packages:

	```
	apt-get isntall fbi omxplayer libav-tools python-pygame
	```

2. Install the following python modules:

	```
	pip install flask youtube-dl
	```

3. Run `server.py` as root

	```
	sudo ./server.py
	```

## API

You can communicate with your Pimass instance using any client capable of performing simple HTTP requests. The accepted commands are the following: 


### POST `/play`

Playback the given video URL.

This request will stop any currently active playback, display a loading screen and a thumbnail if specified. When there are enough data, the video stream will start.

#### Request

```json
{
	"url": "http://domain.com/video.mp4",
	"direct": false,
	"thumb": "http://domain.com/path/to/thumbnail.jpg
}
```

* **url**: The URL to the filename or to the page that contains the media (ex. `http://youtube.com/?v=xxx`)
* **direct**: If set to `true` the link is assumed to be a direct link to the media and `curl` will be used to download it.
* **thumb**: An optional path to an image to be displayed while the video is loading.

#### Response

```json
{
	"status": "ok"
}
```

### GET `/stop`

Interrupt the current playback.

This request forces the player to interrupt the current stream and display the home screen.

#### Response

```json
{
	"status": "ok"
}
```

### GET `/status`

Return the current status of the system.

This request returns the video currently plaging and the status of the individual sub-components.

#### Response

```json
{
	"video": "http://doamin.com/video.mp4",
	"components": {
		"network": "idle",
		"player": "idle"
	}
}
```

* **video**: Points to the URL of the currently playing video, or `null` if there is none.
* **components.netwrok**: The status of the network streamer
* **components.player**: The status of the media player.

The last two fields can have one of the following values:

* `idle`: Component inactive
* `start`: The component is instructed to start
* `run`: The component is running
* `end`: The component completed successfully
* `abort`: The component was force to abort
* `error`: The component was aborted due to an error

## License

Copyright 2016 Ioannis Charalampidis

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
