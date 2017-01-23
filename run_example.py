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