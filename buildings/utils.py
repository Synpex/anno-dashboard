from pyproj import Transformer


def rd_to_wgs(x, y):
    # Create a transformer object for converting RD (EPSG:28992) to WGS84 (EPSG:4326)
    transformer = Transformer.from_crs("epsg:28992", "epsg:4326", always_xy=True)

    # Perform the transformation (longitude, latitude)
    lon, lat = transformer.transform(x, y)
    return lat, lon