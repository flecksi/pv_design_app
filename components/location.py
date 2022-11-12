from pydantic import BaseModel


class Geolocation(BaseModel):
    lat: float = None
    lon: float = None
    ele: float = None
    tz_str: str = None
    address: str = None
    opti_angle_matrix: list = None
    opti_azi_vect: list = None
    opti_tilt_vect: list = None

    @property
    def ready(self) -> bool:
        return (
            isinstance(self.lat, float)
            and isinstance(self.lon, float)
            and isinstance(self.ele, float)
            and isinstance(self.tz_str, str)
        )
