from flask import Flask, request, jsonify
from geodesy.distance import haversine
from geodesy.area import area_of_polygon
from geodesy.azimuth import azimuth
from geodesy.transformations import geodetic_to_utm, utm_to_geodetic
from geodesy.coordinates import new_coordinates
from geodesy.conversions import convert_distance, decimal_to_dms, dms_to_decimal

print("Todos os pacotes foram importados com sucesso!")
