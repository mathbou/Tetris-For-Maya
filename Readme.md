# <img src="resources/logo.png"  width="30" height="auto"> Tetris for Maya

[TOC]

## ⚙ Installation

> [!important] 
> Requires Maya 2022+

As the project is build as a package, you can install it using `mayapy` and `pip`.

- Win:
  `mayapy.exe -m pip install tetris-maya --extra-index-url https://gitlab.com/api/v4/projects/5153531/packages/pypi/simple --target %USERPROFILE%\Documents\maya\<MAYA_VERSION>\prefs\scripts`
- Lnx:
  `mayapy -m pip install tetris-maya --extra-index-url https://gitlab.com/api/v4/projects/5153531/packages/pypi/simple --target ~/maya/<MAYA_VERSION>/prefs/scripts`

#### 📦 Alternative Installation

> [!warning] 
> This method only works for V1/2/3

You could also download the source code from [here](https://gitlab.com/mathbou/TetrisMaya/-/archive/master/TetrisMaya-master.zip?path=V3/tetris_maya)
and unzip the `tetris_maya` folder to your maya script folder

- Win: `%USERPROFILE%\maya\<MAYA_VERSION>\prefs\scripts`
- Lnx: `~/maya/<MAYA_VERSION>/prefs/scripts`

### 🧙‍ Backport 2017-2022

A backport of the game for Maya 2017-2020 is available in
the [backport-27](https://gitlab.com/mathbou/TetrisMaya/-/tree/backport_27) branch.

It can be installed with the standard [installation](#installation) process, 
but you need to replace the package name `tetris-maya` by `tetris-maya-backport`.

The [alternative installation](#alternative-installation) is also doable by downloading the source code
from [here](https://gitlab.com/mathbou/TetrisMaya/-/archive/backport_27/TetrisMaya-backport_27.zip?path=tetris_maya),
and unzipping the `tetris_maya` folder into your maya script folder.

> [!caution] 
> This backport was partially made using automatic converters, so it may be unstable or crash.

## 📚 Add shelf

In the script editor:

```python
import tetris_maya

tetris_maya.install_shelf()
```

## 🎹 Keybindings

| Action         | Key         |
|----------------|-------------|
| Left           | Left Arrow  | 
| Right          | Right Arrow | 
| Soft Drop      | Down Arrow  | 
| Hard Drop      | Space       | 
| Rotate Left    | Z           | 
| Rotate Right   | Up Arrow    | 
| Hold           | C           | 
| Quit (V4 only) | ESC         | 

---

## Why 4 different versions? 🤔

They're here mostly for curiosity purposes and to see my evolution along the years.

### V1 (2016) 🚲

This is the original version I made for a school project back in 2016.
The only instruction given by my teacher was "Entertain me.". I just started Python very recently at the time,
and we had barely a week to give him something. So with my student innocence, I tell myself:
> Hey, why not try to replicate a tetris game and make it playable, what could possibly go wrong ? 🤡

Turns out, not much sleep, but a very good grade and a lot learned along the way.

Due to technical limitations, it runs only on **Maya 2016 or lower**.  
This is due to major changes in the 2017 version, when Autodesk upgrades from Qt4 to Qt5.
On old Maya versions, even if a code loop was running, we were still able to catch hotkey without any additional thread.

### V2 (2018) 🏎️

This version is almost a complete rewrite, made in 2018.
The primary goal of this one was to make it playable on **Maya 2017-2020**.

The major challenge was to find a way to catch the keyboard while the code was running in the main thread of Maya.
My knowledge of PySide2 and threading in general was quite limited, so I chose to use an external catcher that rely on
Pynput.
Obviously, this was a big drawback, as now it needed a dependency to run correctly.

I also made a demo of this version:
[![](https://i.vimeocdn.com/video/690160903-08e3d87193b5eb570c2c877c1ef455a92e5eafcbd4e90138c4c6957e1db628ee-d)](https://vimeo.com/261212280)

### V3 (2022) 🚀

And again, another big rewrite. But why go back to this project in 2022, after 4 years? Well, there are three reasons:

First: Maya finally uses Python 3.7+, so it's an occasion to rewrite the project using more modern syntax and keep
learning while doing it.

Second: I still wanted to get rid of Pynput, and made it completely dependency-free.
This part actually took a lot of thinking and a big change in the game loop architecture.

Finally, the most important one, I wanted to share it 😃 Until now, I wasn't comfortable enough to publish the code,
mostly because I find it ugly.
Also, there were technical concerns; the [V1](#v1) was unusable due to its age,
and the [V2](#v2) was too hard to install for the average user.

### V4 (2025) 🦀

Here we are, 2025, and I still come back at it, except this time the challenge was much bigger.
For years, I thought it would be great to try learning another language and explore different programming paradigms 👨‍💻
At some point, I had this "silly" idea to try learning Rust, and what better (harder? 🤡) project to start the journey with than this one?
It wasn’t a totally random choice either: I knew Python and Rust could work together... but I also knew that they were very, very different from each other 😰

Needless to say, my nearly 10 years of Python experience didn’t help much here. The grammar and philosophy of Rust are
so different, it felt like starting from scratch again, and that's without mentioning the IDE and compiler yelling at me
all day.
At least I'm glad I made this experiment in the AI era; if I didn't use it to generate code, having it as a
teacher/reviewer was really helpful for explaining my mistakes. Thanks to that, instead of taking me maybe a month, 
just took me over a week, from not knowing Rust to building a Python/Rust wheel (and without throwing the computer by the window!).

Now about the project refactor itself: using Rust is, of course, completely overkill from a performance standpoint.
Even with the [V3](#v3), which is pure Python, you'd lose the game long before having speed issues (unless your CPU is
20+ years old).
However, it was a good case to understand how to make both languages work together and share data in both directions.

So that's it, my very first steps as a rustacean... and probably not the last 😀