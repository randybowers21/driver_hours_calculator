from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class PayBand:
    low_hours: int
    high_hours: int
    pay: int

class Fleet(ABC):
    def __init__(self):
        self.rings = []

    @abstractmethod
    def create_all_bands(self) -> None:
        pass
    
class Daily(Fleet):
    def __init__(self):
        super().__init__()
        self.name = 'Daily'
        self.create_all_bands()

    def create_all_bands(self):
        self.rings.append(PayBand(0, 24, 225))

class California(Fleet):
    def __init__(self):
        super().__init__()
        self.name = 'California'
        self.create_all_bands()
    
    def create_all_bands(self):
        self.rings.append(PayBand(0, 8, 160))
        self.rings.append(PayBand(8, 11, 225))
        self.rings.append(PayBand(11, 14, 275))
        self.rings.append(PayBand(14, 24, 325))

class Utah(Fleet):
    def __init__(self):
        super().__init__()
        self.name = 'Utah'
        self.create_all_bands()
    
    def create_all_bands(self):
        self.rings.append(PayBand(0, 8, 160))
        self.rings.append(PayBand(8, 11, 205))
        self.rings.append(PayBand(11, 14, 250))
        self.rings.append(PayBand(14, 24, 275))

class CentPerMile(Fleet):
    def __init__(self):
        super().__init__()
        self.name = 'CPM'
        self.create_all_bands()
    def create_all_bands(self) -> None:
        self.rings.append(PayBand(0,100,0))
        
class FleetFactory(ABC):
    """Factory that returns a fleet class dependant on name input."""
    def get_fleet(self, fleet_name: str) -> Fleet:
        fleets = {
            'Daily': Daily(),
            'Utah': Utah(),
            'California': California(),
            'Cent Per Mile': CentPerMile()
        }
        return fleets[fleet_name]