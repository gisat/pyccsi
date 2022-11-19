ptr-metagen

### Description 
Python package for request and download data from CCSI 

### Install
```
pip install pyccsi
```

### Usage

Import of the downloader class
```
from pyccsi import CCSIDownloader
```
Initialization of the downloader class. Class expecting only one parameter that is the base/host url of CCSI server instance
```
ccsi = CCSIDownloader(host_url="http://localhost:5000")
```
Downloader method 'send_request' send the request on the CSSI resource endpoin vis. host_url/:resource/... 

Available resources name can be get via get request on the resource parameters endpoint vis. host_url/resources/parameters

Parameter params is a dict of resource parameters in the form of dictionary od pydantic base model. Parameters of 
given resource endpoint are show on resource OpenSearch description dokument vis. host_url/:resource/atom/search/description.xml
```
ccsi.send_request(resource=resource, params=params)
```
Send request can return list of the record requested from the CCSI for aditional sorting and manipulation

####Example of params dictionary
resource: cds_er5
```
    {
        'timeStart': '2021-01-01',
        'timeEnd': '2021-01-10',
        'bbox': '25.067713534286536,35.298035029324204,25.193195594830012,35.347934920842974',
        'custom:camsDataset': 'total_column_water_vapour,10m_u_component_of_wind',
        'custom:hour': '03:00,06:00',
        'custom:format': 'grib'
    }
```
Second downloader method  download accept the path of the folder where the data will be downloaded. 
```
ccsi.download(path=output_directory)
```
Optionaly custom list of the records can be set in the method
```
ccsi.download(path=output_directory, records=records)
```
