# Flight Game

## Importing the game to pycharm
1. Open PyCharm and Click the Button **"Get from VCS"**
<details>
  <img src="https://i.imgur.com/5UNZiup.png">
</details>

2. Paste the link of this repository on the **URL** box `https://github.com/SoaresPT/Flight_game_simulator` then click **Clone** at the bottom
<details>
  <img src="https://i.imgur.com/xM1S3hn.png">
</details>

3. Open `main.py` and you'll see 2 warning messages. One about the python interpreter and another about Packages not being installed.
<details>
  <img src="https://i.imgur.com/vaEaYiQ.png">
</details>
4. Click on Configure Python interpreter and select your python version. In this example we're using Python 3.9 but there shouldn't be any restrictions as for what python version should be used.
<details>
  <img src="https://i.imgur.com/6LOzEnb.png">
</details>

5. To fix the Package requirement not satisfied press the button `Install Requirement`
<details>
<img src="https://i.imgur.com/uDG72P1.png">
</details>

## Executing the game on a terminal shell
It is highly recommended to run the game on a terminal window due to coding practices we've used to clear the terminal in order to simulate animations.
1. Right click the Project Name `Flight_game_simulator` and Click `Copy Path/Reference...` followed by `Absolute Path`
<details>
<img src="https://i.imgur.com/IYH0nu5.png">
<img src="https://i.imgur.com/BVI0udR.png">
</details>
2. Open a terminal window and navigate to that folder.
<details>
<img src="https://i.imgur.com/GDSwP7g.png">
</details>

On windows you can open the start menu and type `cmd` and select the Command Prompt. Type `cd` (give a space after the **d**) and right click on the window to paste the Path you previously copied from Pycharm

Press the `Enter` key and you'll be inside the project's directory. Launch the game by typing `.\main.py` (This may not work if you set PyCharm as the default intreperter) so another way is to run: `python main.py`


## Install

- python 3.10
- pip 22.2.2

Before installing python packages from requirements file make sure postgresql is installed

For Mac users:
```bash
brew install postgresql
brew services start postgresql
```

```bash
pip install -r requirements.txt
```