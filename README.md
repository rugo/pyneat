# PyNEAT
A small experiment where HyperNEat is used to create a neuronal network to play Super Mario Bros.


## How it works
This implementation uses the block buffer of Super Mario Bros. to create inputs based on Marios "sight".

![Marios sight](res/inputs.png)

## How to use
This has only tested been tested on Linux machines. Feel free to port it.

To use this, you need to compile my small abstraction lib [libnesfrontend](http://github.com/rugo/libnesfrontend) and a libretro NES core, preferably [QuickNES](https://github.com/libretro/QuickNES_Core).

Compile both of them and copy them into the ``clibs`` folder:

```bash
cp libretro_quicknes.so gaming/clibs/libretrones.so
cp libnesfrontend.so gaming/clibs/
```

Make sure the library is called ``libretrones.so``.

If you want to use this on windows, you have to change the ``emulator.NES`` class to use a [DLL instead](https://docs.python.org/3/library/ctypes.html#loading-dynamic-link-libraries).