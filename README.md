touchosc2midi
==============================================================
> a TouchOSC Bridge clone, aimed at linux, written in python.

Motivation
----------
I wanted to have a TouchOSC Bridge running on a raspberrypi. After researching the options and running into several
deadends, I figured out, I need to write my own. Specifically this program aims to achieve the following:

- it works on linux
- it works on ARM
- it doesn't need the `.touchosc` layout-files
- it can provide virtual midi ports, like the original TouchOSC Bridge from http://hexler.net/software/touchosc
- it is open source
- it advertises the service via `zeroconf`
- it needs minimal configuration

Dependencies
------------
`touchosc2midi` is built on top of these pip-installable packages:

- `pyliblo3` (a maintained fork of `pyliblo` for Python 3)
- `mido` (needs `python-rtmidi` for virtual midi ports)
- `zeroconf`

and without these, it wouldn't be such an embarrassingly trivial program.

It requires Python 3.7+ and is tested on recent Ubuntu releases.

Installation
------------

### Prerequisites
You will need a recent version of `pip`:

    pip install -U pip

Recent versions of `pyliblo3` and `python-rtmidi` ship pre-built binary
wheels, so a plain `pip install` works out of the box on most systems. If
no wheel is available for your platform, pip will build from source and you
will need the OS development libraries `liblo-dev` and `librtmidi-dev`
(Debian/Ubuntu), plus a C compiler:

    sudo apt-get install build-essential liblo-dev librtmidi-dev

### From source

    git clone https://github.com/velolala/touchosc2midi
    cd touchosc2midi
    pip install .

Using a virtual environment is recommended on modern, externally-managed
distributions:

    python3 -m venv venv
    . venv/bin/activate
    pip install .

Getting started
---------------
After installation you should have a the `touchosc2midi` script in your path. Start it with

    touchosc2midi

and open the "Midi Bridge" configuration dialog on your TouchOSC device. You should see an entry for your host. Click on your host and click "Done". Now you should have midi in- and out-ports named "TouchOSC Bridge" that you can use with your client software.

Midi Configuration
------------------
This section shows you, how to do more specific midi configurations.

### Backends

Since `touchosc2midi` uses `mido`, it can be configured with several backends (see:
https://mido.readthedocs.io/en/latest/backends/index.html for details).

By default it tries to mimic the behavior of the original `TouchOSC Bridge` (see: http://hexler.net/software/touchosc); that is: opening virtual in- and out-ports named "TouchOSC Bridge". Therefore, it tries to use an `rtmidi` backend by default, since only this backend allows the creation of virtual midi ports.

Unfortunately, it get's more confusing, because `rtmidi` allows several API's (e.g. 'LINUX_ALSA', 'UNIX_JACK').
The default for `touchosc2midi` is to use the `rtmidi` backend with the first available/implemented API.

If you want to change the backend, the command:

    touchosc2midi list backends

lists the available full backend strings that you can use for the `MIDO_BACKEND=...` environment variable.
To make use of another backend, call `touchosc2midi` like this:

    MIDO_BACKEND=<backend string> touchosc2midi

On a JACK-based rig (e.g. with `mod-host` / MOD Audio), select the JACK API so
the `TouchOSC Bridge` ports appear in the JACK graph and can be wired to other
JACK MIDI clients:

    MIDO_BACKEND=mido.backends.rtmidi/UNIX_JACK touchosc2midi

This is exactly what the bundled systemd service (see *Running as a service*
below) does.

### Midi Ports

By default `touchosc2midi` uses virtual ports for midi-in and midi-out. You can, however, connect midi-ports directly. The command:

    touchosc2midi list ports

lists all available ports with their ID and their port string. You can connect midi-in and midi-out ports either by ID or by their name string, e.g.:

    touchosc2midi --midi-in=1 --midi-out="iConnectMIDI4+ MIDI 11"

Please note, that it is currently not possible to mix virtual and direct midi ports (but I'd be happy to accept your PR for this!).

OSC Configuration
-----------------
`touchosc2midi` tries to detect your main network interface for the network part automatically and you can expect this to work in most cases. You can, however, make it listen on a specific IP address:

    touchosc2midi --ip=192.168.0.53

Running as a service (systemd)
------------------------------
To keep the bridge running permanently (e.g. on a MOD Audio / pi-stomp box
where `jackd` and `mod-host` already run as systemd services), a unit file is
provided in `systemd/touchosc2midi.service`.

It runs the bridge as a JACK MIDI client (`MIDO_BACKEND=mido.backends.rtmidi/UNIX_JACK`)
so its `TouchOSC Bridge` ports show up in the JACK graph, and it auto-connects
its MIDI output to `mod-host:midi_in` on start.

Edit the `User`/`Group` and the `ExecStart` path to match your install, then:

    sudo cp systemd/touchosc2midi.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable --now touchosc2midi.service

    systemctl status touchosc2midi        # check state
    journalctl -u touchosc2midi -f        # follow logs

The service creates its MIDI ports and advertises over zeroconf immediately,
then idles waiting for the first packet from a TouchOSC device.

Docker
------

The git repository contains a `Dockerfile`. To use it:

    docker build -t touchosc2midi:latest -f docker/Dockerfile .

(run from the repository root so the build context includes the sources).

Above builds a container with all OS dependencies and `touchosc2midi` installed. When `run`ning, you will need to share the `/dev/snd/seq` device and expose the OSC receiving port, e.g. like this:

    docker run -p 0.0.0.0:12101:12101/udp --device=/dev/snd/seq:/dev/snd/seq touchosc2midi:latest

Note, that when using docker, the `zeroconf` service announcement does not work, so you'll have to configure your ip address manually on the touchOSC device.


License
-------
This program is published under the MIT License. See `LICENSE` for details.
