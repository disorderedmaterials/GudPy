from copy import deepcopy


class RunContainersAsSamples:
    """
    Class for running containers as samples.
    
    ...

    Attributes
    ----------
    gudrunFile : GudrunFile
        Reference GudrunFile object.

    Methods
    -------
    convertContainers()
        Converts the containers to samples.
    runContainersAsSamples(path='', headless=False)
        Runs containers as samples.
    """
    def __init__(self, gudrunFile):
        """
        Sets up the attributes for the RunContainersAsSamples class.

        Paremeters
        ----------
        gudrunFile : GudrunFile
            Reference GudrunFile object.
        """
        self.gudrunFile = deepcopy(gudrunFile)

    def convertContainers(self):
        """
        Converts containers to samples.
        """
        containersAsSamples = []
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            for sample in sampleBackground.samples:
                for container in sample.containers:
                    containersAsSamples.append(
                        container.convertToSample()
                    )
            sampleBackground.samples = containersAsSamples

    def runContainersAsSamples(self, path='', headless=False):
        """
        Converts containers to samples, and then processes said samples.

        Parameters
        ----------
        path : str, optional
            Path to write to, for Gudrun to use.
        headless : bool, optional
            Is his a headless process?

        Returns
        -------
        subprocess.CompletedProcess | (QProcess, self.write_out, [path, False])
            The result of calling gudrun_dcs using subprocess.run, if headless.
            Otherwise, a QProcess, and intermediate function to call with arguments.        
        """
        self.convertContainers()
        return self.gudrunFile.dcs(path=path, headless=headless)
