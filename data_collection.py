import ee
ee.Authenticate()
ee.Initialize(project='wiai-krishi-dss')
districtList = ['Barwani', 'Jhabua', 'Dindori', 'Alirajpur',
       'Narsimhapur', 'Singrauli', 'Seoni', 'Rewa', 'Rajgarh', 'Panna',
       'Chhindwara', 'Bhind', 'Gwalior', 'Shivpuri', 'Sheopur', 'Damoh',
       'Mandsaur', 'Chhatarpur', 'Sehore', 'Vidisha', 'Sagar', 'Ratlam',
       'Guna', 'Neemuch', 'Mandla', 'Jabalpur', 'West Nimar', 'Satna',
       'Betul', 'Dewas', 'Indore', 'Harda', 'Raisen', 'Hoshangabad',
       'Morena', 'Dhar', 'Burhanpur', 'Niwari', 'Bhopal', 'Datia',
       'Sidhi', 'Shajapur', 'Katni', 'Tikamgarh', 'Shahdol', 'Dhule',
       'Chitrakoot', 'Anuppur', 'Balaghat', 'Agar Malwa', 'Umaria',
       'Jhalawar', 'Ujjain', 'Lalitpur', 'East Nimar', 'Banda',
       'Chittaurgarh']

def addNDVI(image):
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    return image.addBands(ndvi)

def getGreenest(start_date, end_date, dist):
    collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
                    .filterDate(start_date, end_date) \
                    .filterBounds(dist)
    return collection.map(addNDVI).qualityMosaic('NDVI').select(bands).clip(dist)

def getNDVI(greenest):
    return greenest.normalizedDifference(['B8', 'B4'])

import time  # Import the time module for sleep

def exportToCloudStorage(stacked_ndvi, fileName, dist):
    fileNamePrefix = 'tiff_files' + '/' + fileName
    scaled = stacked_ndvi.multiply(100).add(100).uint8()
    task = ee.batch.Export.image.toCloudStorage(image=scaled,
                                                description=fileName,
                                                fileNamePrefix=fileNamePrefix,
                                                bucket='bucket-kdss-ml-dev-data',
                                                region=dist.geometry(),
                                                scale=10,
                                                maxPixels=1e13,
                                                fileFormat='GeoTIFF')
    task.start()
    
    print("Exporting", fileName, "to Cloud Storage...")
    
    if task.status()["state"] == "FAILED":
        print("Error message:", task.status()["error_message"])

bands = ['B2', 'B3', 'B4', 'B8', 'B11', 'B12']

for distName in districtList:
    dist = ee.FeatureCollection('projects/wiai-krishi-dss/assets/INDIA_DISTRICTS') \
            .filter(ee.Filter.eq('dtname', distName))
    startYear = 2023
    startMonth = 10 
    startDate = 1  # Start date either 1 or 16
    fns = 11
    stackedNDVI = None

    for i in range(fns):
        start_date = ee.Date.fromYMD(startYear, startMonth, startDate)

        if startDate == 1:
            startDate = 16
        else:
            startDate = 1
            startMonth += 1
            if startMonth == 13:
                startYear += 1
                startMonth = 1

        end_date = ee.Date.fromYMD(startYear, startMonth, startDate)

        greenest = getGreenest(start_date, end_date, dist)
        ndvi = getNDVI(greenest)

        if i == 0:
            stackedNDVI = ndvi
        else:
            stackedNDVI = stackedNDVI.addBands(ndvi)

    exportToCloudStorage(stackedNDVI, distName.replace(' ', '') + '_rabi_2024', dist)