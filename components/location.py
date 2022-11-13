from pydantic import BaseModel
import numpy as np


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

    def get_opti_matrix(
        self, monthly_weather_factors: list[float]
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        opti_matrix_3d = np.array(self.opti_angle_matrix)
        opti_max = -1
        opti_matrix_2d = np.zeros(
            (len(self.opti_azi_vect) + 1, len(self.opti_tilt_vect))
        )
        for i in range(len(self.opti_azi_vect) + 1):
            for j in range(len(self.opti_tilt_vect)):
                if i >= len(self.opti_azi_vect):
                    opti = sum(opti_matrix_3d[0, j, :] * monthly_weather_factors)
                else:
                    opti = sum(opti_matrix_3d[i, j, :] * monthly_weather_factors)

                opti_matrix_2d[i, j] = opti
                opti_max = max(opti_max, opti)

        opti_matrix_2d = opti_matrix_2d / opti_max * 100.0

        return (
            np.array(self.opti_azi_vect + [360]),
            np.array(self.opti_tilt_vect),
            opti_matrix_2d,
        )
