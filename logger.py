class Logger:
    """
    Logger instance to write continuous measurements to file

    Attributes
    ----------
    file : File
        The file to write to
    """

    def __init__(self, file_path):
        """
        Initializes a new logger instance
        
        Parameters
        ----------
        file_path : str
            Path to the logging file
        """

        self.file = open(file_path, 'w')

        self.file.write(
            'Alarm events,Control events,Avg. alarm wait,Avg. control wait,Max alarm wait,Max control wait\n')

    def write(self, message):
        """
        Write to the file

        Parameters
        ----------
        message : str
            Message to write to the file
        """

        self.file.write(message)

    def close(self):
        """ Close the file handler """

        self.file.close()
