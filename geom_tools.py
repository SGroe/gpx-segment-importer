from qgis.core import QgsDistanceArea
import math


class GeomTools:
    def __init__(self):
        pass

    wgs84_a = 6378137.000
    wgs84_b = 6356752.314
    wgs84_f = (wgs84_a - wgs84_b) / wgs84_a

    @staticmethod
    def calculate_speed(time_a, time_b, point_a, point_b):
        distance = GeomTools.distance(point_a, point_b) / 1000

        time_diff_h = (time_b - time_a).total_seconds() / 3600
        return float(distance / time_diff_h)

    @staticmethod
    def calculate_duration(time_a, time_b):
        duration = (time_b - time_a).total_seconds()
        if float(duration):
            return duration
        return None

    @staticmethod
    def distance(start, end):
        distance = QgsDistanceArea()
        # distance.setEllipsoidalMode(True)
        distance.setEllipsoid('WGS84')
        return distance.measureLine(start, end)

    @staticmethod
    def distance_andoyer(start, end):
        """
        https://de.wikibooks.org/wiki/Astronomische_Berechnungen_f%C3%BCr_Amateure/_Distanzen/_Erdglobus#Abstand_zweier_Punkte_auf_der_Erdoberfl.C3.A4che
        https://de.wikipedia.org/wiki/Henri_Andoyer
        :param start: start coordinate
        :param end: end coordinate
        :return:
        """

        lambda_a = math.radians(start.x())
        phi_a = math.radians(start.y())
        lambda_b = math.radians(end.x())
        phi_b = math.radians(end.y())

        f = (phi_a + phi_b) / 2
        g = (phi_a - phi_b) / 2
        ll = (lambda_a - lambda_b) / 2

        if g == 0 and ll == 0:
            return 0

        squ_sin_l = math.pow(math.sin(ll), 2)
        squ_cos_l = math.pow(math.cos(ll), 2)
        squ_sin_g = math.pow(math.sin(g), 2)
        squ_cos_g = math.pow(math.cos(g), 2)
        squ_sin_f = math.pow(math.sin(f), 2)
        squ_cos_f = math.pow(math.cos(f), 2)

        s = squ_sin_g * squ_cos_l + squ_cos_f * squ_sin_l
        c = squ_cos_g * squ_cos_l + squ_sin_f * squ_sin_l

        w = math.atan(math.sqrt(s / c))

        r = math.sqrt(s * c) / w

        d = 2 * w * GeomTools.wgs84_a

        h1 = (3 * r - 1) / (2 * c)
        h2 = (3 * r + 1) / (2 * s)

        d = d * (1 + GeomTools.wgs84_f * h1 * squ_sin_f * squ_cos_g - GeomTools.wgs84_f * h2 * squ_cos_f * squ_sin_g)

        if float(d):
            return d
        else:
            print ("distance between track points result is not a number")
            return 0.0
