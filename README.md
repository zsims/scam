# scam
Basic framework for creating headless motion detected security camera systems that runs on any hardware.

It's intended to be flexible enough

# Development
 1. Install requirements: `pip install -r requirements`
 2. Run tests: `python -m unittest`

# Running
With 'scam' installed, you need to provide a 'run' script.

## Example
Example of watching a camera constantly and uploading photos to Dropbox hourly, or if motion is detected:
```python

from scam import source, sink, detect, pipe
import datetime

runner = pipe.MultiLoopRunner([
    [
        source.IpCamera('Sample', '192.168.1.30'),
        pipe.Any([
            detect.ContourMatcher(minimum_area=300, show_bounding_box=True),
            detect.IntervalMatcher(time_delta=datetime.timedelta(hours=1)),
        ]),
        sink.DropboxSink(
            path_prefix='/Cameras/Photos/',
            access_token='My Access Token'
        ),
        sink.LoggerSink()
    ]
])

runner.run()
```

With the following results:

**Frame 1**

![Frame1](https://raw.github.com/zsims/scam/master/scam/test/resources/snapshot1.jpg)

**Frame 2**

![Frame2](https://raw.github.com/zsims/scam/master/scam/test/resources/snapshot1.jpg)

**Match with Bounding Box**

![Match with Bounding Box](https://raw.github.com/zsims/scam/master/scam/test/resources/match.jpg)

## Running as a Service
It may be useful to run scam as a service to ensure scam is running all the time. scam doesn't include this, as it's easy to get from your system.

 * Windows - [NSSM](https://nssm.cc/), or similar
 * Linux, using Systemd per below

## Linux

 1. Create a Systemd Unit File: `$ vim /lib/systemd/system/scam.service`
 
 2. Fill it out (this may change slightly if using [Virtualenv](https://virtualenv.pypa.io/en/stable/))
```
[Unit]
Description=Scam
After=multi-user.target

[Service]
Type=idle
ExecStart=/usr/bin/python3 /home/me/run.py

[Install]
WantedBy=multi-user.target
```

 3. Chmod the Unit file: `$ sudo chmod 644 /lib/systemd/system/scam.service`
 4. Enable: `$ sudo systemctl enable scam.service`

# FAQ
1. Does scam support video input?

> Not really. Only via "snapshots" for now.

2. Why not Zoneminder or similar?

> Zoneminder isn't really modular, nor headless. This can thus be used for remote deployments that may be behind a CGNAT, and thus not able to expose a web interface.

3. What's with the `pipe` stuff?

> I needed this to be highly modular as the requirements/steps were ever evolving.
