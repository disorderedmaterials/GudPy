from copy import deepcopy


class RunContainersAsSamples:

    def __init__(self, gudrunFile):

        self.gudrunFile = deepcopy(gudrunFile)

    def convertContainers(self):
        containersAsSamples = []
        for sampleBackground in self.gudrunFile.sampleBackgrounds:
            for sample in sampleBackground.samples:
                for container in sample.containers:
                    containersAsSamples.append(
                        self.gudrunFile.convertToSample(
                            container
                        )
                    )
            sampleBackground.samples = containersAsSamples

    def runContainersAsSamples(self, path='', headless=False):
        self.convertContainers()
        return self.gudrunFile.dcs(path=path, headless=headless)
