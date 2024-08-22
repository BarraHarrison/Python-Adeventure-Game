import pickle

# Puzzle class
class Puzzle:
    def __init__(self, question, solution):
        self.question = question
        self.solution = solution
        self.solved = False

    def ask(self):
        print(self.question)
        answer = input("> ").strip().lower()
        if answer == self.solution.lower():
            print("Correct! The puzzle is solved.")
            self.solved = True
        else:
            print("That's not correct.")

# Item class
class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __str__(self):
        return f"{self.name}: {self.description}"

# Room class
class Room:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.items = []
        self.exits = {}
        self.locked_exits = {}

    def add_item(self, item):
        self.items.append(item)

    def set_exit(self, direction, room, locked=False, puzzle=None, key=None):
        self.exits[direction] = room
        if locked:
            self.locked_exits[direction] = {"puzzle": puzzle, "key": key}

    def __str__(self):
        exits = ", ".join(self.exits.keys())
        locked_exits = ", ".join([f"{direction} (locked)" for direction in self.locked_exits.keys()])
        return (f"{self.name}\n\n{self.description}\n\nItems: {', '.join([item.name for item in self.items])}\n"
                f"Exits: {exits}\nLocked Exits: {locked_exits}")

# Player class
class Player:
    def __init__(self, name):
        self.name = name
        self.current_room = None
        self.inventory = []

    def move(self, direction):
        if direction in self.current_room.exits:
            if direction in self.current_room.locked_exits:
                locked_exit = self.current_room.locked_exits[direction]
                if locked_exit["puzzle"] and not locked_exit["puzzle"].solved:
                    print("The door is locked. You need to solve a puzzle to open it.")
                    locked_exit["puzzle"].ask()
                    if locked_exit["puzzle"].solved:
                        print("The door unlocks.")
                        del self.current_room.locked_exits[direction]
                elif locked_exit["key"]:
                    if any(item.name.lower() == locked_exit["key"].lower() for item in self.inventory):
                        print("You use the key to unlock the door.")
                        del self.current_room.locked_exits[direction]
                    else:
                        print("The door is locked, and you need a key to unlock it.")
                        return
            if direction in self.current_room.exits:
                self.current_room = self.current_room.exits[direction]
                print(f"You move {direction} to the {self.current_room.name}.")
        else:
            print("You can't go that way.")

    def take_item(self, item_name):
        for item in self.current_room.items:
            if item.name.lower() == item_name.lower():
                self.inventory.append(item)
                self.current_room.items.remove(item)
                print(f"You take the {item.name}.")
                return
        print(f"There is no {item_name} here.")

    def show_inventory(self):
        if not self.inventory:
            print("You are carrying nothing.")
        else:
            print("You are carrying:")
            for item in self.inventory:
                print(f"- {item.name}")

    def __str__(self):
        return self.name

# Game class
class Game:
    def __init__(self):
        self.player = None
        self.rooms = {}

    def create_world(self):
        # Create Puzzles
        riddle_puzzle = Puzzle(
            "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?",
            "Echo"
        )

        second_riddle_puzzle = Puzzle(
            "I’m light as a feather, yet the strongest man can’t hold me for more than 5 minutes. What am I?",
            "Breath"
        )

        # Create Rooms
        living_room = Room("Living Room", "A cozy room with a couch and a TV.")
        kitchen = Room("Kitchen", "A clean kitchen with a fridge and a stove.")
        bedroom = Room("Bedroom", "A small room with a bed and a wardrobe.")
        secret_room_1 = Room("Secret Room", "A hidden room filled with treasures.")
        secret_room_2 = Room("Secret Room 2", "An even more hidden room with more mysteries.")
        treasure_chamber = Room("Treasure Chamber", "The final room filled with the most valuable treasures.")

        # Create Items
        key = Item("Key", "A small golden key.")
        ancient_key = Item("Ancient Key", "A very old and ornate key.")

        # Add items to the rooms
        kitchen.add_item(key)
        secret_room_2.add_item(ancient_key)

        # Set room exits
        living_room.set_exit("north", kitchen)
        kitchen.set_exit("south", living_room)
        living_room.set_exit("east", bedroom)
        bedroom.set_exit('west', living_room)

        # Locked exit to the first secret room with a riddle puzzle
        bedroom.set_exit("north", secret_room_1, locked=True, puzzle=riddle_puzzle)

        # Locked exit to the second secret room with a different riddle puzzle
        secret_room_1.set_exit("north", secret_room_2, locked=True, puzzle=second_riddle_puzzle)

        # Locked exit to the Treasure Chamber that requires an ancient key
        secret_room_2.set_exit("north", treasure_chamber, locked=True, key="Ancient Key")

        # Store rooms in a dictionary
        self.rooms = {
            "living_room": living_room,
            "kitchen": kitchen,
            "bedroom": bedroom,
            "secret_room_1": secret_room_1,
            "secret_room_2": secret_room_2,
            "treasure_chamber": treasure_chamber
        }

        # Set initial player location
        self.player = Player("Hero")
        self.player.current_room = living_room

    def save_game(self, filename="savegame.pkl"):
        with open(filename, 'wb') as f:
            pickle.dump(self, f)
        print("Game saved.")

    def load_game(self, filename="savegame.pkl"):
        with open(filename, 'rb') as f:
            game = pickle.load(f)
        return game

    def parse_command(self, command):
        if command in ["north", "south", "east", "west"]:
            self.player.move(command)
        elif command.startswith("take "):
            item_name = command[5:].strip()
            if item_name:
                self.player.take_item(item_name)
            else:
                print("Take what?")
        elif command == "inventory":
            self.player.show_inventory()
        elif command == "look":
            print(self.player.current_room)
        elif command == "save":
            self.save_game()
        elif command == "load":
            new_game = self.load_game()
            self.__dict__.update(new_game.__dict__)
            print(f"Game loaded. You are in the {self.player.current_room.name}.")
        elif command == "quit":
            print("Thanks for playing!")
            return False  # indicate that the player wants to quit
        else:
            print("I don't understand that command.")
        return True  # Indicate that the game should continue

    def start(self):
        print("Welcome to the Adventure Game!")
        print(f"You are in the {self.player.current_room.name}.")
        while True:
            command = input("> ").lower().strip()
            should_continue = self.parse_command(command)
            if not should_continue:
                break  # exit the loop if the player wants to quit

        # End of game message
        if self.player.current_room.name == "Treasure Chamber":
            print("Congratulations! You've reached the Treasure Chamber and completed the adventure!")
            print("Thank you for playing!")

# Main game loop
if __name__ == "__main__":
    game = Game()
    choice = input("Do you want to start a new game or load a saved game? (new/load) ").strip().lower()
    if choice == "load":
        game = game.load_game()
    else:
        game.create_world()
    game.start()
