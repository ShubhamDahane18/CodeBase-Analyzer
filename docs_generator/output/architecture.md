# System Architecture Overview
================================

The system architecture of this Python project is designed to implement a simple game using the Turtle graphics library. The game involves two players, each with their own turtle, and a set of rules for movement and scoring.

## High-Level System Components

* **Game Engine**: The core component responsible for managing the game workflow, including player initialization, turn management, and scoring.
* **Turtle Graphics Library**: A dependency used to create the game environment and handle user input.
* **Random Number Generator**: A dependency used to generate random numbers for the game.
* **Mathematical Operations**: A dependency used for mathematical operations.

## High-Level Data Flow / Pipeline
--------------------------------

The game workflow is as follows:

1. **Initialization**: The game engine initializes two players, each with their own turtle.
2. **Turn Management**: The game engine enters a loop where each player takes turns moving their turtle.
3. **Projectile Firing**: Each player's turn consists of firing a projectile (a yellow circle) towards the other player's turtle.
4. **Collision Detection**: The game engine checks if the projectile hits the other player's turtle.
5. **Scoring**: If the projectile hits the other player's turtle, the game increments the score for the player who fired the projectile.
6. **Game Over**: The game continues until one player reaches a score of 200.

## Core Modules and Responsibilities
-----------------------------------

### Chase.py

* **Module Overview**: The `Chase.py` module implements the game engine, responsible for managing the game workflow.
* **Responsibilities**:
	+ Initialize two players, each with their own turtle.
	+ Manage player turns and projectile firing.
	+ Detect collisions and update scores.
	+ Handle game over conditions.

## Interactions between Major Components
--------------------------------------

* **Game Engine**: Interacts with the Turtle Graphics Library to create the game environment and handle user input.
* **Game Engine**: Interacts with the Random Number Generator to generate random numbers for the game.
* **Game Engine**: Interacts with the Mathematical Operations to perform mathematical operations.

## Design Patterns Observed
---------------------------

* **Model-View-Controller (MVC)**: The game engine acts as the controller, managing the game workflow and interacting with the view (Turtle Graphics Library) and model (game state).
* **Dependency Injection**: The game engine depends on the Turtle Graphics Library, Random Number Generator, and Mathematical Operations, which are injected as dependencies.
* **Single Responsibility Principle (SRP)**: The `Chase.py` module has a single responsibility, implementing the game engine and managing the game workflow.