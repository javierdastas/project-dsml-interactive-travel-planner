def convert_coordinates(lat_dms, lon_dms):

    def dms_to_decimal(degrees, minutes, seconds, direction):
        decimal = degrees + minutes / 60 + seconds / 3600
        if direction in ['S', 'W']:  # South and West indicate negative values
            decimal *= -1
        return decimal

    def parse_dms(dms_str):
        dms_str = dms_str.replace("°", " ").replace("′", " ").replace("″", " ")
        parts = dms_str.strip().split()
    
        if len(parts) == 2:  # Solo grados y dirección
            degrees = int(parts[0])
            minutes = 0
            seconds = 0
            direction = parts[1]
        elif len(parts) == 3:  # Grados, minutos y dirección
            degrees = int(parts[0])
            minutes = int(parts[1])
            seconds = 0
            direction = parts[2]
        elif len(parts) == 4:  # Grados, minutos, segundos y dirección
            degrees = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2])
            direction = parts[3]
        else:
            raise ValueError(f"Invalid DMS format: {dms_str}")
    
        if direction not in ['N', 'S', 'E', 'W']:
            raise ValueError(f"Invalid direction in DMS: {direction}")

        return degrees, minutes, seconds, direction



    lat_degrees, lat_minutes, lat_seconds, lat_direction = parse_dms(lat_dms)
    lon_degrees, lon_minutes, lon_seconds, lon_direction = parse_dms(lon_dms)

    latitude = dms_to_decimal(lat_degrees, lat_minutes, lat_seconds, lat_direction)
    longitude = dms_to_decimal(lon_degrees, lon_minutes, lon_seconds, lon_direction)

    return latitude, longitude
