# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 11:49:00 2016

@author: acollin
"""

import os

import utm
import pandas as pd
import numpy as np
from shapely.geometry import Point

this_dir = os.path.dirname(os.path.realpath(__file__))
installation_dir = os.path.join(this_dir, "installation")

### Equipment
file_path = os.path.join(installation_dir, 'logisticsDB_equipment_python.xlsx')
xls_file = pd.ExcelFile(file_path, encoding = 'utf-8')
sheet_names = xls_file.sheet_names

equipment_rov= xls_file.parse(sheet_names[0])
equipment_divers = xls_file.parse(sheet_names[1])
equipment_cable_burial = xls_file.parse(sheet_names[2])
equipment_excavating = xls_file.parse(sheet_names[3])
equipment_mattress = xls_file.parse(sheet_names[4])
equipment_rock_filter_bags = xls_file.parse(sheet_names[5])
equipment_split_pipe = xls_file.parse(sheet_names[6])
equipment_hammer = xls_file.parse(sheet_names[7])
equipment_drilling_rigs = xls_file.parse(sheet_names[8])
equipment_vibro_driver = xls_file.parse(sheet_names[9])

### Ports
file_path = os.path.join(installation_dir, 'logisticsDB_ports_python.xlsx')
xls_file = pd.ExcelFile(file_path, encoding = 'utf-8')
ports = xls_file.parse()

port_names = ports["Name"]
port_x = ports.pop("UTM x")
port_y = ports.pop("UTM y")
port_utm = ports.pop("UTM zone")

port_points = []

for x, y, zone_str in zip(port_x, port_y, port_utm):
    
    zone_number_str, zone_letter = zone_str.split()
    lat, lon = utm.to_latlon(x, y, int(zone_number_str), zone_letter)
    point = Point(lon, lat)
    port_points.append(point)
    
port_locations = {name: point for name, point in zip(port_names, port_points)}

### Vessels
file_path = os.path.join(installation_dir, 'logisticsDB_vessel_python.xlsx')
xls_file = pd.ExcelFile(file_path, encoding = 'utf-8')
helicopter_df = xls_file.parse(sheetname="Helicopter")
ahts_df = xls_file.parse(sheetname="AHTS")
multicat_df = xls_file.parse(sheetname="Multicat")
barge_df = xls_file.parse(sheetname="Barge")
crane_barge_df = xls_file.parse(sheetname="Crane Barge")
crane_vessel_df = xls_file.parse(sheetname="Crane Vessel")
csv_df = xls_file.parse(sheetname="CSV")
ctv_df = xls_file.parse(sheetname="CTV")
clb_df = xls_file.parse(sheetname="CLB")
clv_df = xls_file.parse(sheetname="CLV")
jackup_barge_df = xls_file.parse(sheetname="Jackup Barge")
jackup_vssel_df = xls_file.parse(sheetname="Jackup Vessel")
tugboat_df = xls_file.parse(sheetname="Tugboat")

### Site
bathy_table = pd.read_csv(os.path.join(installation_dir, 'aegirbath2.txt'),
                          delimiter="\t",
                          header=None)
                        
soil_grid = pd.read_csv(os.path.join(installation_dir, 'aegirsoil3.txt'),
                        delimiter="\t",
                        header=None)

Z1=bathy_table[2]
dZ=soil_grid[3]

Z=np.array([Z1.values,(Z1-dZ).values]).T
sediment = np.array([soil_grid[2].values,soil_grid[4].values]).T
x_max = bathy_table.max()[0]
y_max = bathy_table.max()[1]
x_min = bathy_table.min()[0]
y_min = bathy_table.min()[1]

nx=144
ny=176

dx = (x_max-x_min)/(nx-1)
dy = (y_max-y_min)/(ny-1)

x= np.linspace(x_min , x_max , nx)
y = np.linspace(y_min , y_max , ny)
[X,Y] = np.meshgrid(x,y)

bathy_table[0]=np.ravel(X)
bathy_table[1]=np.ravel(Y)

layers = (1,)

depth_layers = []
sediment_layers = []

for z in layers:
    depths = []
    sediments = []
    
    for y_count in y:
        
        d = []
        s = []
        
        for x_count in x:
            
            point_df = bathy_table[(bathy_table[0] == x_count) &
                                   (bathy_table[1] == y_count)].index[0]
            
            d.append(Z[point_df,z])
            s.append(sediment[point_df,z])
                
        depths.append(d)
        sediments.append(s)
        
    depth_layers.append(depths)
    sediment_layers.append(sediments)
    
depth_array = np.swapaxes(np.array(depth_layers, dtype=float), 0, 2)
sediment_array = np.swapaxes(np.array(sediment_layers), 0, 2)

layer_names = ["layer {}".format(x_layers) for x_layers in layers]

strata = strata={"values": {"depth": depth_array,
                            'sediment': sediment_array},
                 "coords": [x, y, layer_names]}

lease_utm_zone = \
    "+proj=utm +zone=30 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"

### Metocean
file_path = os.path.join(installation_dir, 'inputs_user.xlsx')
xls_file = pd.ExcelFile(file_path, encoding = 'utf-8')
metocean = xls_file.parse('metocean', index_col = 0)

fmtStr = "%Y-%m-%d %H:%M:%S.%f"
datetime_index_dict = {'year': metocean['year'],
                       'month': metocean['month'],
                       'day' : metocean['day'],
                       'hour' : metocean['hour']}

wave_series = metocean.loc[:, ['Hs', 'Tp']]
wave_series['DateTime'] = pd.to_datetime(datetime_index_dict, format = fmtStr)
#wave_series = wave_series.set_index(["DateTime"])

tidal_series = metocean.loc[:, ['Cs']]
tidal_series['DateTime'] = pd.to_datetime(datetime_index_dict, format =fmtStr)
#tidal_series = tidal_series.set_index(["DateTime"])

wind_series = metocean.loc[:, ['Ws']]
wind_series['DateTime'] = pd.to_datetime(datetime_index_dict, format = fmtStr)
#wind_series = wind_series.set_index(["DateTime"])

### Device
device = xls_file.parse('device', index_col = 0)

system_type = device['type'].values.item()
system_length = device['length'].values.item()
system_width = device['width'].values.item()
system_height = device['height'].values.item()
system_mass = device['dry mass'].values.item()
assembly_duration = device['assembly duration'].values.item()
load_out_method = device['load out'].values.item()
transportation_method = device['transportation method'].values.item()
bollard_pull = device['bollard pull'].values.item()
connect_duration = device['connect duration'].values.item()
disconnect_duration = device['disconnect duration'].values.item()
project_start_date = pd.to_datetime(device['Project start date'].values.item())
project_start_date = project_start_date.to_datetime()
#sub_systems = device['sub system list'].values.item()
installation_limit_Hs = device['max Hs'].values.item()
installation_limit_Tp = device['max Tp'].values.item()
installation_limit_Ws = device['max wind speed'].values.item()
installation_limit_Cs = device['max current speed'].values.item()

### Subdevice
sub_device = xls_file.parse('sub_device')

### Landfall
landfall = xls_file.parse('landfall', index_col = 0)

### Rates
file_path = os.path.join(installation_dir, 'equipment_perf_rates.xlsx')
xls_file = pd.ExcelFile(file_path, encoding = 'utf-8')

equipment_penetration_rates = xls_file.parse('penet')
installation_soil_compatibility = xls_file.parse('laying')
temp_other = xls_file.parse('other')

surface_laying_rate = temp_other[temp_other.index ==
    'Surface laying [m/h]'].values[0][0]
split_pipe_laying_rate = temp_other[temp_other.index ==
    'Installation of iron cast split pipes [m/h]'].values[0][0]
loading_rate = temp_other[temp_other.index ==
    'Loading rate [m/h]'].values[0][0]
grout_rate = temp_other[temp_other.index ==
    'Grout rate [m3/h]'].values[0][0]
fuel_cost_rate = temp_other[temp_other.index ==
    'Fuel cost rate [EUR/l]'].values[0][0]
port_percentage_cost = temp_other[temp_other.index ==
    'Port percentual cost [%]'].values[0][0]
comissioning_time = temp_other[temp_other.index ==
    'Comissioning time [weeks]'].values[0][0]
cost_contingency = temp_other[temp_other.index ==
    'Cost Contingency [%]'].values[0][0]

### Safety factors
file_path = os.path.join(installation_dir, 'safety_factors.xlsx')
xls_file = pd.ExcelFile(file_path, encoding = 'utf-8')

port_sf = xls_file.parse('port_sf', index_col = 0)
vessel_sf = xls_file.parse('vessel_sf', index_col = 0)
equipment_sf = xls_file.parse('eq_sf', index_col = 0)

### Configuration options
# installation order
file_path = os.path.join(installation_dir, 'installation_order_0.xlsx')
xls_file = pd.ExcelFile(file_path, encoding = 'utf-8')
installation_order = xls_file.parse('InstallationOrder', index_col = 0)
# lease area entry point
file_path = os.path.join(installation_dir, 'inputs_user.xlsx')
xls_file = pd.ExcelFile(file_path, encoding = 'utf-8')
entry_point = xls_file.parse('entry_point', index_col = 0)

x = entry_point.loc[:, 'x coord'].item()
y = entry_point.loc[:, 'y coord'].item()

entry_point_shapely = Point(x,y)

### Hydrodynamic
layout_dict = {'device001': [585500.0, 6650000.0, 0.0]}

### Electrical
electrical_network = {}
electrical_network['topology'] = {}
electrical_network['nodes'] = {}

electrical_components = {'Key Identifier': {},
                         'Installation Type' : {},
                         'Quantity' : {},	
                         'UTM X' : {},
                         'UTM Y' : {},
                         'Marker' : {}}

electrical_components_df = pd.DataFrame(electrical_components)

cable_routes = {'Key Identifier' : {},
                'Burial Depth' : {},
                'Split Pipe' : {},
                'UTM X' : {},
                'UTM Y' : {},
                'Marker' : {}}

cable_routes_df = pd.DataFrame(cable_routes)

substations = {'Substation Identifier' : {},
               'Type' : {},
               'Mass' : {},
               'Volume' : {},
               'Length' : {},
               'Width' : {},
               'Height' : {},
               'Profile' : {},
               'Wet Frontal Area' : {},
               'Wet Beam Area' : {},
               'Dry Frontal Area' : {},
               'Dry Beam Area' : {},
               'Surface Roughness' : {},
               'Orientation Angle' : {},
               'Marker' : {}}

substations_df = pd.DataFrame(substations)

umbilicals = {'Key Identifier' : {},
              'Length' : {},
              'Dry Mass' : {},
              'Required Floatation' : {},
              'Floatation Length' : {},
              'Marker' : {}}

umbilicals_df = pd.DataFrame(umbilicals)
### M & F
mf_network = {}
mf_network['topology'] = {}
mf_network['nodes'] = {}

foundations_data = {'Type' : {},
                    'Sub-Type' : {},
                    'UTM X' : {},
                    'UTM Y' : {},
                    'Depth' : {},
                    'Length' : {},
                    'Width' : {},
                    'Height' : {},
                    'Installation Depth' : {},
                    'Dry Mass' : {},
                    'Grout Type' : {},
                    'Grout Volume' : {},
                    'Marker' : {}}

foundations_data_df = pd.DataFrame(foundations_data)

foundations_layers = {'Layer Number' : {},
                      'Soil Type' : {},
                      'Depth' : {},
                      'Marker' : {}}

foundations_layers_df = pd.DataFrame(foundations_layers)

moorings_data = {'Line Identifier' : {},
                 'Marker' : {}}

moorings_data_df = pd.DataFrame(moorings_data)

line_data = {'Line Identifier' : {},
             'Type' : {},
             'Length' : {},
             'Dry Mass' : {}}

line_data_df = pd.DataFrame(line_data)
             
# collect together
test_data = {"component.rov" : equipment_rov,
             "component.divers" : equipment_divers,
             "component.cable_burial" : equipment_cable_burial,
             "component.excavating" : equipment_excavating,
             "component.mattress_installation" : equipment_mattress,
             "component.rock_bags_installation" : equipment_rock_filter_bags,
             "component.split_pipes_installation" : equipment_split_pipe,
             "component.hammer" : equipment_hammer,
             "component.drilling_rigs" : equipment_drilling_rigs,
             "component.vibro_driver" : equipment_vibro_driver,
             "component.vehicle_helicopter": helicopter_df,
             "component.vehicle_vessel_ahts": ahts_df,
             "component.vehicle_vessel_multicat": multicat_df,
             "component.vehicle_vessel_crane_barge": crane_barge_df,
             "component.vehicle_vessel_barge": barge_df,
             "component.vehicle_vessel_crane_vessel": crane_vessel_df,
             "component.vehicle_vessel_csv": csv_df,
             "component.vehicle_vessel_ctv": ctv_df,
             "component.vehicle_vessel_clb": clb_df,
             "component.vehicle_vessel_clv": clv_df,
             "component.vehicle_vessel_jackup_barge": jackup_barge_df,
             "component.vehicle_vessel_jackup_vessel": jackup_vssel_df,
             "component.vehicle_vessel_tugboat": tugboat_df,
             "component.ports" : ports,
             "component.port_locations": port_locations,

             "project.electrical_network" : electrical_network,
             "project.electrical_component_data" : electrical_components_df,
             "project.cable_routes" : cable_routes_df,
             "project.substation_props" : substations_df,
             "project.umbilical_cable_data" : umbilicals_df,

             "project.moorings_foundations_network" : mf_network,
             "project.foundations_component_data" : foundations_data_df,
             "project.foundations_soil_data" : foundations_layers_df,
             "project.moorings_component_data" : moorings_data_df,
             "project.moorings_line_data" : line_data_df,

             "farm.installation_order" : installation_order,
             "component.equipment_penetration_rates" :
                 equipment_penetration_rates,
             "component.installation_soil_compatibility" :
                 installation_soil_compatibility,
             "project.surface_laying_rate" : surface_laying_rate,
             "project.split_pipe_laying_rate" : split_pipe_laying_rate,
             "project.loading_rate" : loading_rate,
             "project.grout_rate" : grout_rate,
             "project.fuel_cost_rate" : fuel_cost_rate,

             "project.port_percentage_cost" : port_percentage_cost,
             "farm.comissioning_time" : comissioning_time,
             
             "farm.cost_contingency" : cost_contingency,
             
             "project.port_safety_factors" : port_sf,
             "project.vessel_safety_factors" : vessel_sf,
             "component.equipment_safety_factors" : equipment_sf,
             "project.lease_area_entry_point" : entry_point_shapely,
             "project.layout" : layout_dict,

             "device.system_type" : system_type,
             "device.system_length" : system_length,
             "device.system_width" : system_width,
             "device.system_height" : system_height,
             "device.system_mass": system_mass,
             "device.assembly_duration" : assembly_duration,
             "device.load_out_method" : load_out_method,
             "device.transportation_method" : transportation_method,
             "device.bollard_pull" : bollard_pull,
             "device.connect_duration" : connect_duration,
             "device.disconnect_duration" : disconnect_duration,
             "project.start_date" : project_start_date,
             
             "device.subsystem_installation" : sub_device,

             "device.installation_limit_Hs" : installation_limit_Hs,
             "device.installation_limit_Tp" : installation_limit_Tp,
             "device.installation_limit_Ws" : installation_limit_Ws,
             "device.installation_limit_Cs" : installation_limit_Ws,
             
             "farm.wave_series_installation" : wave_series,
             "farm.tidal_series_installation" : tidal_series,
             "farm.wind_series_installation" : wind_series,
             
             "bathymetry.layers" : strata,
             
             "installation_delete.landfall" : landfall,
             
             "site.projection" : lease_utm_zone,

             }

if __name__ == "__main__":

    from dtocean_core.utils.files import pickle_test_data

    file_path = os.path.abspath(__file__)
    pkl_path = pickle_test_data(file_path, test_data)
    
    print "generate test data: {}".format(pkl_path)
