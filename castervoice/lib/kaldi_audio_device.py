import sys

import sounddevice


def _describe_device(index, device_info):
    hostapi_name = sounddevice.query_hostapis(device_info["hostapi"])["name"]
    return f"{device_info['name']}, {hostapi_name}"


def resolve_audio_input_device(device_spec):
    try:
        device_index = int(device_spec)
        device_info = sounddevice.query_devices(device_index)
    except ValueError:
        device_info = sounddevice.query_devices(device_spec)
        device_index = None
        for index, candidate in enumerate(sounddevice.query_devices()):
            if candidate["name"] == device_info["name"] and candidate["hostapi"] == device_info["hostapi"]:
                device_index = index
                break
        if device_index is None:
            raise ValueError(f"Unable to determine PortAudio index for {device_spec!r}")

    if device_info["max_input_channels"] <= 0:
        description = _describe_device(device_index, device_info)
        raise ValueError(f"Device {description!r} is not an input device")

    return device_index, device_info


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 1:
        print("Usage: python -m castervoice.lib.kaldi_audio_device <device-index-or-name>", file=sys.stderr)
        return 2

    device_spec = argv[0]
    try:
        device_index, _ = resolve_audio_input_device(device_spec)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(device_index)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
