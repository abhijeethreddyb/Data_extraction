from shapely import wkt
from shapely.wkt import loads

# Function to clean district names if necessary
def get_tiff_filename(district_name):
    suffix="_rabi_2024.tif"
    cleaned_district_name = ''.join(district_name.split())
    return f"{cleaned_district_name}{suffix}"

# Function to extract NDVI values from the TIFF stack for a single point
def extract_ndvi_values_for_point(src, point,fns):
    row, col = src.index(point.x, point.y)
    # Read the data for given layers at the given point
    fn = min(src.count,fns)
    try:
      ndvi_values = [src.read(i+1, window=rasterio.windows.Window(col, row, 1, 1))[0, 0]for i in range(fn)]
      for _ in range(fns-src.count): vh_values.insert(0,0)
    except:
      ndvi_values = [0 for _ in range(fns)]

    return ndvi_values

if isinstance(data.iloc[0]['geometry'], str):
    data['geometry'] = data['geometry'].apply(loads)

# Convert the DataFrame to a GeoDataFrame
gdf = gp.GeoDataFrame(data, geometry='geometry')

# Initialize an empty list to store the SAVI matrix
ndvi_matrix = []
prev_district = None
src = None

for idx, row in gdf.iterrows():
    current_district = row['district']
    if(current_district != prev_district):
        print(current_district)
        if src:  
              src.close()
        tiff_filename = get_tiff_filename(current_district)
        tiff_path = '/bucket-kdss-ml-dev-data/tiff_files/' + tiff_filename
        src = rasterio.open(tiff_path)
        prev_district = current_district


    ndvi_values = extract_ndvi_values_for_point(src, row['geometry'],11)
    ndvi_matrix.append(ndvi_values)

# Close the last opened TIFF file
if src:
    src.close()


data.shape[0] == len(ndvi_matrix)
ndvi_columns = ['oct_1f','oct_2f','nov_1f','nov_2f','dec_1f','dec_2f','jan_1f','jan_2f','feb_1f','feb_2f','mar_1f']

ndvi_df = pd.DataFrame(ndvi_matrix, columns=ndvi_columns)

final_df = pd.concat([data,ndvi_df],axis = 1)