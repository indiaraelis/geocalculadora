from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pyproj
from pyproj import datadir
datadir.set_data_dir("/usr/share/proj")
import math
from typing import Dict, Any, Tuple, List, Optional
import os

# Se estiver usando variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuração detalhada dos datums com parâmetros geodésicos precisos
DATUM_PARAMS = {
    'WGS84': {
        'a': 6378137.0,           # Semi-eixo maior (metros)
        'rf': 298.257223563,      # Achatamento recíproco
        'epsg': 4326,             # EPSG para coordenadas geográficas
        'name': 'World Geodetic System 1984'
    },
    'SIRGAS2000': {
        'a': 6378137.0,
        'rf': 298.257222101,
        'epsg': 4674,
        'name': 'Sistema de Referência Geocêntrico para as Américas 2000'
    },
    'SAD69': {
        'a': 6378160.0,
        'rf': 298.25,
        'epsg': 4618,
        'name': 'South American Datum 1969'
    },
    'CORREGO_ALEGRE': {
        'a': 6378388.0,           # Corrigido: era 6378384.0
        'rf': 297.0,
        'epsg': 4225,
        'name': 'Córrego Alegre 1970-72'
    }
}

class GeoCalculatorError(Exception):
    """Exceção personalizada para erros de cálculo geográfico"""
    pass

def validate_coordinate(lat: float, lon: float) -> bool:
    """Valida se as coordenadas estão dentro dos limites válidos"""
    return -90 <= lat <= 90 and -180 <= lon <= 180

def validate_numeric_input(value: Any, param_name: str, min_val: float = None, max_val: float = None) -> float:
    """Valida e converte entrada numérica"""
    try:
        num_value = float(value)
        if math.isnan(num_value) or math.isinf(num_value):
            raise GeoCalculatorError(f"{param_name} deve ser um número válido")
        
        if min_val is not None and num_value < min_val:
            raise GeoCalculatorError(f"{param_name} deve ser maior que {min_val}")
        
        if max_val is not None and num_value > max_val:
            raise GeoCalculatorError(f"{param_name} deve ser menor que {max_val}")
            
        return num_value
    except (ValueError, TypeError):
        raise GeoCalculatorError(f"{param_name} deve ser um número válido")

def get_geodesic(datum: str) -> pyproj.Geod:
    """Cria objeto geodésico para o datum especificado"""
    params = DATUM_PARAMS.get(datum, DATUM_PARAMS['WGS84'])
    return pyproj.Geod(a=params['a'], rf=params['rf'])

def calculate_utm_zone(longitude: float) -> int:
    """Calcula a zona UTM baseada na longitude"""
    return int((longitude + 180) // 6) + 1

def get_utm_epsg(zone: int, hemisphere: str, datum: str = 'WGS84') -> int:
    """Retorna o código EPSG correto para UTM baseado na zona, hemisfério e datum"""
    if datum == 'SIRGAS2000':
        # SIRGAS2000 UTM zones para Brasil (zonas 18N a 25S)
        if hemisphere == 'Sul':
            return 31972 + zone  # Base EPSG para SIRGAS2000 UTM Sul
        else:
            return 31972 + zone - 60  # Ajuste para hemisfério norte
    else:
        # WGS84 UTM zones
        if hemisphere == 'Sul':
            return 32700 + zone  # Base EPSG para WGS84 UTM Sul
        else:
            return 32600 + zone  # Base EPSG para WGS84 UTM Norte

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calcular_distancia', methods=['POST'])
def calcular_distancia():
    """Calcula a distância geodésica entre dois pontos"""
    try:
        data = request.get_json()
        if not data:
            raise GeoCalculatorError("Dados não fornecidos")
        
        # Validação de entrada
        lat1 = validate_numeric_input(data.get('lat1'), 'Latitude 1', -90, 90)
        lon1 = validate_numeric_input(data.get('lon1'), 'Longitude 1', -180, 180)
        lat2 = validate_numeric_input(data.get('lat2'), 'Latitude 2', -90, 90)
        lon2 = validate_numeric_input(data.get('lon2'), 'Longitude 2', -180, 180)
        datum = data.get('datum', 'WGS84')
        
        if datum not in DATUM_PARAMS:
            raise GeoCalculatorError(f"Datum '{datum}' não suportado")
        
        # Cálculo da distância
        geod = get_geodesic(datum)
        azimute1, azimute2, distancia = geod.inv(lon1, lat1, lon2, lat2)
        
        return jsonify({
            'success': True,
            'distancia_metros': round(distancia, 3),
            'distancia_km': round(distancia / 1000, 3),
            'azimute_direto': round(azimute1, 3),
            'azimute_inverso': round(azimute2, 3),
            'datum_usado': datum
        })
        
    except GeoCalculatorError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': 'Erro interno no cálculo da distância'}), 500

@app.route('/calcular_area', methods=['POST'])
def calcular_area():
    """Calcula a área de um polígono (mínimo 3 pontos)"""
    try:
        data = request.get_json()
        if not data:
            raise GeoCalculatorError("Dados não fornecidos")
        
        datum = data.get('datum', 'WGS84')
        if datum not in DATUM_PARAMS:
            raise GeoCalculatorError(f"Datum '{datum}' não suportado")
        
        # Aceita tanto formato de triângulo (A, B, C) quanto array de pontos
        pontos = []
        
        if 'pontos' in data:
            # Formato de array de pontos
            for i, ponto in enumerate(data['pontos']):
                lat = validate_numeric_input(ponto.get('lat'), f'Latitude do ponto {i+1}', -90, 90)
                lon = validate_numeric_input(ponto.get('lon'), f'Longitude do ponto {i+1}', -180, 180)
                pontos.append((lat, lon))
        else:
            # Formato legado (triângulo)
            lat_a = validate_numeric_input(data.get('latA'), 'Latitude A', -90, 90)
            lon_a = validate_numeric_input(data.get('lonA'), 'Longitude A', -180, 180)
            lat_b = validate_numeric_input(data.get('latB'), 'Latitude B', -90, 90)
            lon_b = validate_numeric_input(data.get('lonB'), 'Longitude B', -180, 180)
            lat_c = validate_numeric_input(data.get('latC'), 'Latitude C', -90, 90)
            lon_c = validate_numeric_input(data.get('lonC'), 'Longitude C', -180, 180)
            pontos = [(lat_a, lon_a), (lat_b, lon_b), (lat_c, lon_c)]
        
        if len(pontos) < 3:
            raise GeoCalculatorError("São necessários pelo menos 3 pontos para calcular a área")
        
        # Separar latitudes e longitudes
        lats = [p[0] for p in pontos]
        lons = [p[1] for p in pontos]
        
        # Cálculo da área e perímetro
        geod = get_geodesic(datum)
        area, perimetro = geod.polygon_area_perimeter(lons, lats)
        area = abs(area)  # Área sempre positiva
        
        return jsonify({
            'success': True,
            'area_m2': round(area, 3),
            'area_km2': round(area / 1_000_000, 6),
            'area_hectares': round(area / 10_000, 4),
            'perimetro_m': round(perimetro, 3),
            'perimetro_km': round(perimetro / 1000, 3),
            'num_pontos': len(pontos),
            'datum_usado': datum
        })
        
    except GeoCalculatorError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': 'Erro interno no cálculo da área'}), 500

@app.route('/calcular_azimute', methods=['POST'])
def calcular_azimute():
    """Calcula o azimute entre dois pontos"""
    try:
        data = request.get_json()
        if not data:
            raise GeoCalculatorError("Dados não fornecidos")
        
        # Aceita tanto formato novo quanto legado
        lat1 = validate_numeric_input(
            data.get('lat1') or data.get('azimute_latitude1'), 
            'Latitude 1', -90, 90
        )
        lon1 = validate_numeric_input(
            data.get('lon1') or data.get('azimute_longitude1'), 
            'Longitude 1', -180, 180
        )
        lat2 = validate_numeric_input(
            data.get('lat2') or data.get('azimute_latitude2'), 
            'Latitude 2', -90, 90
        )
        lon2 = validate_numeric_input(
            data.get('lon2') or data.get('azimute_longitude2'), 
            'Longitude 2', -180, 180
        )
        datum = data.get('datum', 'WGS84')
        
        if datum not in DATUM_PARAMS:
            raise GeoCalculatorError(f"Datum '{datum}' não suportado")
        
        geod = get_geodesic(datum)
        azimute_direto, azimute_inverso, distancia = geod.inv(lon1, lat1, lon2, lat2)
        
        # Converter azimute para 0-360°
        if azimute_direto < 0:
            azimute_direto += 360
        if azimute_inverso < 0:
            azimute_inverso += 360
        
        return jsonify({
            'success': True,
            'azimute_direto': round(azimute_direto, 3),
            'azimute_inverso': round(azimute_inverso, 3),
            'distancia_m': round(distancia, 3),
            'distancia_km': round(distancia / 1000, 3),
            'datum_usado': datum
        })
        
    except GeoCalculatorError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': 'Erro interno no cálculo do azimute'}), 500

@app.route('/calcular_utm', methods=['POST'])
def calcular_utm():
    """Converte coordenadas geográficas para UTM"""
    try:
        data = request.get_json()
        if not data:
            raise GeoCalculatorError("Dados não fornecidos")
        
        latitude = validate_numeric_input(data.get('latitude'), 'Latitude', -90, 90)
        longitude = validate_numeric_input(data.get('longitude'), 'Longitude', -180, 180)
        datum = data.get('datum', 'WGS84')
        
        if datum not in DATUM_PARAMS:
            raise GeoCalculatorError(f"Datum '{datum}' não suportado")
        
        # Calcular zona UTM e hemisfério
        zona = calculate_utm_zone(longitude)
        hemisferio = "Norte" if latitude >= 0 else "Sul"
        
        # Obter EPSG correto para UTM
        epsg_geografico = DATUM_PARAMS[datum]['epsg']
        epsg_utm = get_utm_epsg(zona, hemisferio, datum)
        
        # Converter coordenadas
        transformer = pyproj.Transformer.from_crs(
            f"EPSG:{epsg_geografico}", 
            f"EPSG:{epsg_utm}", 
            always_xy=True
        )
        easting, northing = transformer.transform(longitude, latitude)
        
        return jsonify({
            'success': True,
            'zona_utm': zona,
            'hemisferio': hemisferio,
            'datum': datum,
            'easting': round(easting, 3),
            'northing': round(northing, 3),
            'epsg_utm': epsg_utm,
            'fuso': f"{zona}{hemisferio[0]}"  # Ex: "23S"
        })
        
    except GeoCalculatorError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': 'Erro interno na conversão UTM'}), 500

@app.route('/calcular_novas_coordenadas', methods=['POST'])
def calcular_novas_coordenadas():
    """Calcula novas coordenadas baseado em ponto de partida, distância e azimute"""
    try:
        data = request.get_json()
        if not data:
            raise GeoCalculatorError("Dados não fornecidos")
        
        lat = validate_numeric_input(data.get('lat'), 'Latitude', -90, 90)
        lon = validate_numeric_input(data.get('lon'), 'Longitude', -180, 180)
        distancia = validate_numeric_input(data.get('distancia'), 'Distância', 0)
        azimute = validate_numeric_input(data.get('azimute'), 'Azimute', 0, 360)
        datum = data.get('datum', 'WGS84')
        
        if datum not in DATUM_PARAMS:
            raise GeoCalculatorError(f"Datum '{datum}' não suportado")
        
        geod = get_geodesic(datum)
        lon2, lat2, azimute_final = geod.fwd(lon, lat, azimute, distancia)
        
        return jsonify({
            'success': True,
            'lat': round(lat2, 8),
            'lon': round(lon2, 8),
            'azimute_final': round(azimute_final, 3),
            'datum_usado': datum
        })
        
    except GeoCalculatorError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': 'Erro interno no cálculo de novas coordenadas'}), 500

@app.route('/calcular_conversao', methods=['POST'])
def calcular_conversao():
    """Converte unidades de medida"""
    try:
        data = request.get_json()
        if not data:
            raise GeoCalculatorError("Dados não fornecidos")
        
        valor = validate_numeric_input(data.get('valor'), 'Valor', 0)
        origem = data.get('origem', '').strip()
        destino = data.get('destino', '').strip()
        
        # Fatores de conversão precisos
        fatores = {
            ('km', 'milhas'): 0.621371192,
            ('milhas', 'km'): 1.609344,
            ('km', 'metros'): 1000,
            ('metros', 'km'): 0.001,
            ('milhas', 'm_nauticas'): 0.868976,
            ('m_nauticas', 'milhas'): 1.150779,
            ('km', 'm_nauticas'): 0.539956803,
            ('m_nauticas', 'km'): 1.852,
            ('metros', 'pes'): 3.28084,
            ('pes', 'metros'): 0.3048,
            ('metros', 'jardas'): 1.09361,
            ('jardas', 'metros'): 0.9144
        }
        
        fator = fatores.get((origem, destino))
        if fator is None:
            raise GeoCalculatorError(f'Conversão de {origem} para {destino} não suportada')
        
        resultado = valor * fator
        
        return jsonify({
            'success': True,
            'resultado': round(resultado, 6),
            'unidade_origem': origem,
            'unidade_destino': destino,
            'valor_original': valor
        })
        
    except GeoCalculatorError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': 'Erro interno na conversão'}), 500

@app.route('/converter_decimal_para_dms', methods=['POST'])
def converter_decimal_para_dms():
    """Converte coordenadas decimais para graus, minutos, segundos"""
    try:
        data = request.get_json()
        if not data:
            raise GeoCalculatorError("Dados não fornecidos")
        
        valor_decimal = validate_numeric_input(data.get('valorDecimal'), 'Valor decimal', -180, 180)
        
        # Determinar sinal
        sinal = 1 if valor_decimal >= 0 else -1
        valor_abs = abs(valor_decimal)
        
        # Calcular componentes
        graus = int(valor_abs)
        minutos_float = (valor_abs - graus) * 60
        minutos = int(minutos_float)
        segundos = (minutos_float - minutos) * 60
        
        # Aplicar sinal aos graus
        graus *= sinal
        
        return jsonify({
            'success': True,
            'graus': graus,
            'minutos': minutos,
            'segundos': round(segundos, 4),
            'dms_formatado': f"{graus}° {minutos:02d}' {segundos:06.3f}\"",
            'valor_original': valor_decimal
        })
        
    except GeoCalculatorError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': 'Erro interno na conversão DMS'}), 500

@app.route('/converter_dms_para_decimal', methods=['POST'])
def converter_dms_para_decimal():
    """Converte graus, minutos, segundos para coordenadas decimais"""
    try:
        data = request.get_json()
        if not data:
            raise GeoCalculatorError("Dados não fornecidos")
        
        graus = validate_numeric_input(data.get('graus'), 'Graus', -180, 180)
        minutos = validate_numeric_input(data.get('minutos'), 'Minutos', 0, 59)
        segundos = validate_numeric_input(data.get('segundos'), 'Segundos', 0, 59.999)
        
        # Determinar sinal baseado nos graus
        sinal = 1 if graus >= 0 else -1
        graus_abs = abs(graus)
        
        # Calcular decimal
        decimal = (graus_abs + minutos / 60 + segundos / 3600) * sinal
        
        return jsonify({
            'success': True,
            'resultado': round(decimal, 8),
            'componentes': {
                'graus': graus,
                'minutos': minutos,
                'segundos': segundos
            }
        })
        
    except GeoCalculatorError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': 'Erro interno na conversão decimal'}), 500

@app.route('/info_datums', methods=['GET'])
def info_datums():
    """Retorna informações sobre os datums disponíveis"""
    return jsonify({
        'success': True,
        'datums': DATUM_PARAMS
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'success': False, 'error': 'Método HTTP não permitido'}), 405

port = int(os.environ.get("PORT", 5000))  # Render usa uma porta aleatória via env
app.run(host='0.0.0.0', port=port, debug=True)