# commands/base_command.py
import os
from typing import List

"""
TODO 3-1: The BaseCommand class has a show_usage method implemented, but the execute method is not 
implemented and is passed on to the child class. Think about why this difference is made. 완

커맨드마다 excute()를 다르게 구현해야 하기 때문에 BaseCommand에서는 구현하려면 분기를 하거나, 여러 private 변수들을 참조하는 것이 복잡하기 때문이다.


TODO 3-2: The update_current_path method of the BaseCommand class is slightly different from other methods. 
It has a @classmethod decorator and takes a cls argument instead of self. In Python, this is called a 
class method, and think about why it was implemented as a class method instead of a normal method. 완

클래스 메소드는 클래스를 인스턴스화 하지 않고도 호출할 수 있는 메소드이기 때문이다. 
BaseCommand 클래스는 인스턴스화 하지 않고도 update_current_path()를 호출할 수 있어야 하기 때문에 클래스 메소드로 구현되었다.

"""
class BaseCommand:
    """
    Base class for all commands. Each command should inherit from this class and 
    override the execute() method.
    
    For example, the MoveCommand class overrides the execute() method to implement 
    the mv command.

    Attributes:
        current_path (str): The current path. Usefull for commands like ls, cd, etc.
    """

    current_path = os.getcwd()

    @classmethod
    def update_current_path(cls, new_path: str):
        """
        Update the current path.
        You need to understand how class methods work.

        Args:
            new_path (str): The new path. (Must be an relative path)
        """
        BaseCommand.current_path = os.path.join(BaseCommand.current_path, new_path)

    def __init__(self, options: List[str], args: List[str]) -> None:
        """
        Initialize a new instance of BaseCommand.

        Args:
            options (List[str]): The command options (e.g. -v, -i, etc.)
            args (List[str]): The command arguments (e.g. file names, directory names, etc.)
        """
        self.options = options
        self.args = args
        self.description = 'Helpful description of the command'
        self.usage = 'Usage: command [options] [arguments]'

    def show_usage(self) -> None:
        """
        Show the command usage.
        """
        print(self.description)
        print(self.usage)

    def execute(self) -> None:
        """
        Execute the command. This method should be overridden by each subclass.
        """
        raise NotImplementedError