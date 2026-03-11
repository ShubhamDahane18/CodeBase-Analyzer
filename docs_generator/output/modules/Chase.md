**Chase.py**
================

**Module Overview**
-------------------

The `Chase.py` module is a Python script that implements a simple game using the Turtle graphics library. The game involves two players, each with their own turtle, and a set of rules for movement and scoring.

**Architecture / Workflow**
---------------------------

The game workflow is as follows:

1. The game initializes two players, each with their own turtle.
2. The game enters a loop where each player takes turns moving their turtle.
3. Each player's turn consists of firing a projectile (a yellow circle) towards the other player's turtle.
4. If the projectile hits the other player's turtle, the game increments the score for the player who fired the projectile.
5. The game continues until one player reaches a score of 200.

**Dependencies**
----------------

* `turtle`: The Turtle graphics library is used to create the game environment and handle user input.
* `random`: The `random` module is used to generate random numbers for the game.
* `math`: The `math` module is used for mathematical operations.

**Public API (functions/classes)**
-----------------------------------

### Functions

* `drawing()`: Draws a square on the screen.
* `switchturn(t)`: Switches the turn between players.
* `taketurn(t)`: Handles a player's turn, including firing a projectile and moving the turtle.
* `slow(damage, speed)`: Calculates the speed of a player's turtle based on the damage taken and the player's speed.
* `win1()`: Displays a message indicating that player 1 has won.
* `win2()`: Displays a message indicating that player 2 has won.
* `step1()`: Moves player 1's turtle towards the center of the screen.
* `step2()`: Moves player 2's turtle towards the center of the screen.
* `go1a()`: Handles player 1's turn, including firing a projectile and moving the turtle.
* `go1b()`: Handles player 1's turn, including firing a projectile and moving the turtle, but with a higher speed.
* `go2a()`: Handles player 2's turn, including firing a projectile and moving the turtle.
* `go2b()`: Handles player 2's turn, including firing a projectile and moving the turtle, but with a higher speed.
* `nothing()`: A placeholder function that does nothing.
* `fire1()`: Fires a projectile from player 1's turtle towards player 2's turtle.
* `fire2()`: Fires a projectile from player 2's turtle towards player 1's turtle.

### Classes

None.

**Function Documentation**
---------------------------

### `drawing()`

Draws a square on the screen.

```python
def drawing():
    """Draws a square on the screen."""
    square.forward(40)
    square.left(90)
    square.forward(2)
    square.backward(2)
    square.right(90)
```

### `switchturn(t)`

Switches the turn between players.

```python
def switchturn(t):
    """Switches the turn between players."""
    if t == 1:
        return 2
    else:
        return 1
```

### `taketurn(t)`

Handles a player's turn, including firing a projectile and moving the turtle.

```python
def taketurn(t):
    """Handles a player's turn, including firing a projectile and moving the turtle."""
    listen()
    if t == 1:
        onkey(go1a, 'Right')
        onkey(go1b, 'Up')
        onkey(fire1, 'Return')
        onkey(nothing, 'd')
        onkey(nothing, 'w')
    if t == 2:
        onkey(nothing, 'Right')
        onkey(nothing, 'Up')
        onkey(fire2, 'space')
        onkey(go2a, 'd')
        onkey(go2b, 'w')
```

### `slow(damage, speed)`

Calculates the speed of a player's turtle based on the damage taken and the player's speed.

```python
def slow(damage, speed):
    """Calculates the speed of a player's turtle based on the damage taken and the player's speed."""
    return speed - damage
```

### `win1()`

Displays a message indicating that player 1 has won.

```python
def win1():
    """Displays a message indicating that player 1 has won."""
    turt = Turtle()
    turt.pendown()
    turt.ht()
    turt.color('red')
    turt.write('RED WINS', True, 'center', ('Arial', 24, 'normal'))
```

### `win2()`

Displays a message indicating that player 2 has won.

```python
def win2():
    """Displays a message indicating that player 2 has won."""
    turt = Turtle()
    turt.pendown()
    turt.ht()
    turt.color('blue')
    turt.write('BLUE WINS', True, 'center', ('Arial', 24, 'normal'))
```

### `step1()`

Moves player 1's turtle towards the center of the screen.

```python
def step1():
    """Moves player 1's turtle towards the center of the screen."""
    p1.left(90)
    p1.forward(20)
    if p1.xcor() == p2.xcor() and p1.ycor() == p2.ycor():
        win1()
```

### `step2()`

Moves player 2's turtle towards the center of the screen.

```python
def step2():
    """Moves player 2's turtle towards the center of the screen."""
    p2.left(90)
    p2.forward(20)
    if p1.xcor() == p2.xcor() and p1.ycor() == p2.ycor():
        win2()
```

### `go1a()`

Handles player 1's turn, including firing a projectile and moving the turtle.

```python
def go1a():
    """Handles player 1's turn, including firing a projectile and moving the turtle."""
    global turn
    global rnd1
    hit = fire1()
    speed = slow(hit, rnd1)
    for i in range(2 * speed):
        if abs(p1.xcor()) == 200 and abs(p1.ycor()) == 200:
            step1()
        else:
            p1.forward(20)
            if p1.xcor() == p2.xcor() and p1.ycor() == p2.ycor():
                win1()
    turn = switchturn(turn)
    taketurn(turn)
```

### `go1b()`

Handles player 1's turn, including firing a projectile and moving the turtle, but with a higher speed.

```python
def go1b():
    """Handles player 1's turn, including firing a projectile and moving the turtle, but with a higher speed."""
    global turn
    global rnd1
    hit = fire1()
    speed = slow(hit, rnd1) + 1
    for i in range(2 * speed):
        if abs(p1.xcor()) == 200 and abs(p1.ycor()) == 200:
            step1()
        else:
            p1.forward(20)
            if p1.xcor() == p2.xcor() and p1.ycor() == p2.ycor():
                win1()
    turn = switchturn(turn)
    taketurn(turn)
```

### `go2a()`

Handles player 2's turn, including firing a projectile and moving the turtle.

```python
def go2a():
    """Handles player 2's turn, including firing a projectile and moving the turtle."""
    global turn
    global rnd2
    hit = fire2()
    speed = slow(hit, rnd2)
    for i in range(2 * speed):
        if abs(p2.xcor()) == 200 and abs(p2.ycor()) == 200:
            step2()
        else:
            p2.forward(20)
            if p1.xcor() == p2.xcor() and p1.ycor() == p2.ycor():
                win2()
    turn = switchturn(turn)
    taketurn(turn)
```

### `go2b()`

Handles player 2's turn, including firing a projectile and moving the turtle, but with a higher speed.

```python
def go2b():
    """Handles player 2's turn, including firing a projectile and moving the turtle, but with a higher speed."""
    global turn
    global rnd2
    hit = fire2()
    speed = slow(hit, rnd2) + 1
    for i in range(2 * speed):
        if abs(p2.xcor()) == 200 and abs(p2.ycor()) == 200:
            step2()
        else:
            p2.forward(20)
            if p1.xcor() == p2.xcor() and p1.ycor() == p2.ycor():
                win2()
    turn = switchturn(turn)
    taketurn(turn)
```

### `nothing()`

A placeholder function that does nothing.

```python
def nothing():
    """A placeholder function that does nothing."""
    pass
```

### `fire1()`

Fires a projectile from player 1's turtle towards player 2's turtle.

```python
def fire1():
    """Fires a projectile from player 1's turtle towards player 2's turtle."""
    ball = Turtle()
    ball.speed(0)
    ball.penup()
    ball.ht()
    ball.shape('circle')
    ball.shapesize(0.5)
    ball.color('yellow')
    ball.setx(p2.xcor())
    ball.sety(p2.ycor())
    ball.speed(1)
    if p1.xcor() == p2.xcor() or p1.ycor() == p2.ycor():
        ball.st()
        ball.goto(p1.xcor(), p1.ycor())
        ball.ht()
        return 1
    else:
        ball.ht()
        return 0
```

### `fire2()`

Fires a projectile from player 2's turtle towards player 1's turtle.

```python
def fire2():
    """Fires a projectile from player 2's turtle towards player 1's turtle."""
    ball = Turtle()
    ball.speed(0)
    ball.penup()
    ball.ht()
    ball.shape('circle')
    ball.shapesize(0.5)
    ball.color('yellow')
    ball.setx(p1.xcor())
    ball.sety(p1.ycor())
    ball.speed(1)
    if p1.xcor() == p2.xcor() or p1.ycor() == p2.ycor():
        ball.st()
        ball.goto(p2.xcor(), p2.ycor())
        ball.ht()
        return 1
    else:
        ball.ht()
        return 0
```

**Parameters**
--------------

* `damage`: The amount of damage taken by a player's turtle.
* `speed`: The speed of a player's turtle.
* `t`: The turn number, used to switch between players.
* `rnd1` and `rnd2`: Random numbers used to generate the speed of each player's turtle.

**Return Values**
-----------------

* `slow(damage, speed)`: The speed of a player's turtle after taking damage.
* `fire1()` and `fire2()`: 1 if the projectile hits the other player's turtle, 0 otherwise.

**Example Usage**
-----------------

```python
import Chase

# Initialize the game
Chase.drawing()

# Set up the players
p1 = Turtle()
p2 = Turtle()

# Set up the game loop
while True:
    # Handle player 1's turn
    go1a()

    # Handle player 2's turn
    go2a()
```

**Developer Notes**
-------------------

* The game uses the Turtle graphics library to create the game environment and handle user input.
* The game loop is implemented using a while loop that continues until one player reaches a score of 200.
* The `slow(damage, speed)` function calculates the speed of a player's turtle based on the damage taken and the player's speed.
* The `fire1()` and `fire2()` functions fire projectiles from each player's turtle towards the other player's turtle.
* The `go1a()` and `go2a()` functions handle each player's turn, including firing a projectile and moving the turtle.
* The `win1()` and `win2()` functions display a message indicating that one player has won.