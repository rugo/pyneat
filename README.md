# PyNEAT
A small experiment where HyperNeat is used to create a neural network to play Super Mario Bros.


## How it works
This implementation uses the block buffer of Super Mario Bros. to create inputs based on Marios "sight".

![Marios sight](res/inputs.png)

## How to use
This has only been tested on Linux machines and with Python 3. Feel free to port it.

If you're using 64 bit Linux with installed liballegro, you can just run the examples. The library path has to be set to ``gaming/clibs``:

```bash
export LD_LIBRARY_PATH=gaming/clibs
python3 example_play_by_hand.py
```

Otherwise you need to install libalegro 5 (``apt install liballegro5.0`` on Debian), compile my small abstraction lib [libnesfrontend](http://github.com/rugo/libnesfrontend) and a libretro NES core, preferably [QuickNES](https://github.com/libretro/QuickNES_Core). This is described on the [libnesfrontend](http://github.com/rugo/libnesfrontend) page. 

Compile them and copy them into the ``clibs`` folder:

```bash
cp libretro_quicknes.so gaming/clibs/libretrones.so
cp libnesfrontend.so gaming/clibs/
```

Make sure the libretro library (here QuickNES) is called ``libretrones.so``.

If you want to use this on windows, you have to change the ``emulator.NES`` class to use a [DLL instead](https://docs.python.org/3/library/ctypes.html#loading-dynamic-link-libraries).
