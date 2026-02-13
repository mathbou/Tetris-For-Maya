# <img src="resources/logo.png"  width="30" height="auto"> Tetris for Maya

[TOC]

## ⚙ Installation

**{- Requires Maya 2022+ -}**

Copy the `tetris_maya` folder into your maya script folder  
- Win: `%USERPROFILE%\maya\<MAYA_VERSION>\prefs\scripts`
- Lnx: `~/maya/<MAYA_VERSION>/prefs/scripts`

#### 📦 Alternative Installation

As the project is build as a package, you also can install it using the `mayapy` and `pip`.

- Win: `mayapy.exe -m pip install git+https://gitlab.com/mathbou/TetrisMaya.git  --target %USERPROFILE%\maya\<MAYA_VERSION>\prefs\scripts`
- Lnx: `mayapy -m pip install git+https://gitlab.com/mathbou/TetrisMaya.git --target ~/maya/<MAYA_VERSION>/prefs/scripts`

## 📚 Add shelf

In the script editor:

```python
import tetris_maya
tetris_maya.install_shelf()
```

## 🎹 Keybindings

| Action       | Key         |
|--------------|-------------|
| Left         | Left Arrow  | 
| Right        | Right Arrow | 
| Soft Drop    | Down Arrow  | 
| Hard Drop    | Space       | 
| Rotate Left  | Z           | 
| Rotate Right | Up Arrow    | 
| Hold         | C           | 

---

## Why 3 different versions ? 🤔

They're here mostly for curiosity purpose and to see my evolution along the years.

### V1

This is the original version I made for a school project, back in 2016. 
The only instruction given by my teacher was "Entertain me.". I just started python very recently at the time, 
and we had barely a week to give him something. So with my student innocence, I tell myself: 
> Hey, why not try to replicate a tetris game and make it playable, what could possibly go wrong ? 🤡

Turns out, not much sleep, but a very good grade and a lot learned along the way.

Due to technical limitations, it runs only on **Maya 2016 or lower**.  
This is due to major changes in the 2017 version, when Autodesk upgrades from Qt4 to Qt5. 
On old Maya versions, even if a code loop was running, we were still able to catch hotkey without any additional thread.

### V2

This version is almost a complete rewrite, made in 2018.
The primary goal of this one was to make it playable on **Maya 2017-2020**. 

The major challenge was to find a way to catch the keyboard while the code was running in the main thread of Maya.
My knowledge of PySide2 and threading in general was quite limited, so I choose to use an external catcher that rely on Pynput.
Obviously, this was a big drawback, as now it needed a dependency to run correctly.

I also made a demo of this version:
[![](https://i.vimeocdn.com/video/690160903-08e3d87193b5eb570c2c877c1ef455a92e5eafcbd4e90138c4c6957e1db628ee-d)](https://vimeo.com/261212280)

### tetris_maya (V3)

And again, another big rewrite. But why go back on this project after another 4 years ? Well, there are three reasons:

First: Maya finally uses Python 3.7+, so it's an occasion to rewrite the project using more modern syntax and keep learning while doing it.
And if you followed correctly, yes, this version is only compatible with **Maya 2022+**

Second: I still wanted to get rid of Pynput, and made it completely dependency-free. 
This part actually took a lot of thinking and a big change on the game loop architecture.

Third: I wanted to share it 😃 Until now, I wasn't comfortable enough to publish the code, mostly because I find it ugly, and it wasn't reflecting my skills.
Also, there were technical concerns, the [V1](#v1) was unusable due to its age, and the [V2](#v2) was too hard to install.

