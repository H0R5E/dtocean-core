# -*- coding: utf-8 -*-

#    Copyright (C) 2016 'Mathew Topper, Vincenzo Nava, David Bould, Rui Duarte,
#                       'Francesco Ferri, Adam Collin'
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This module contains the package interface to the dtocean-maintenance module.

Note:
  The function decorators (such as '@classmethod', etc) must not be removed.

.. module:: operations
   :platform: Windows
   
.. moduleauthor:: Mathew Topper <mathew.topper@tecnalia.com>
                  Vincenzo Nava <vincenzo.nava@tecnalia.com>
"""

# Built in modules
import os
import pickle
import logging
import datetime

# External 3rd party libraries
import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta

# External DTOcean libraries
from polite.paths import Directory, ObjDirectory, UserDataDirectory
from polite.configuration import ReadINI
from aneris.boundary.interface import MaskVariable
from dtocean_maintenance.main import LCOE_Optimiser
from dtocean_maintenance.input import inputOM

# DTOcean Core modules
from . import ModuleInterface
from .electrical import ElectricalInterface
from .moorings import MooringsInterface
from .installation import InstallationInterface
from .reliability import ReliabilityInterface
from ..utils.maintenance import (get_input_tables,
                                 get_user_network,
                                 get_user_compdict,
                                 get_point_depth,
                                 get_events_table)

# Set up logging
module_logger = logging.getLogger(__name__)


class MaintenanceInterface(ModuleInterface):
    
    '''Interface to the dtocean-maintenance module.

    '''
        
    @classmethod         
    def get_name(cls):
        
        '''A class method for the common name of the interface.
        
        Returns:
          str: A unique string
        '''
        
        return 'Operations and Maintenance'
        
    @classmethod         
    def declare_weight(cls):
        
        return 5

    @classmethod         
    def declare_inputs(cls):
        
        '''A class method to declare all the variables required as inputs by
        this interface. 
        
        Returns:
          list: List of inputs identifiers
        
        Example:
          The returned value can be None or a list of identifier strings which 
          appear in the data descriptions. For example::
          
              inputs = ['My:first:variable',
                        'My:second:variable',
                       ]
        '''

        input_list  =  [
                        'site.projection',
                        "bathymetry.layers",
                        'corridor.layers',
                        
                        "farm.helideck",
                        'farm.tidal_series_installation',
                        'farm.wave_series_installation',
                        'farm.wind_series_installation',

                        "device.system_type",
                        'device.system_length',
                        'device.system_width',
                        'device.system_height',
                        'device.system_mass',

                        'device.assembly_duration',
                        'device.bollard_pull',
                        'device.connect_duration',
                        'device.control_subsystem_installation',
                        'device.disconnect_duration',
                        'device.load_out_method',
                        'device.transportation_method',
                        "device.two_stage_assembly",
                      
                        'device.subsystem_access',
                        'device.subsystem_costs',
                        'device.subsystem_installation',
                        'device.subsystem_failure_rates',
                        'device.subsystem_inspections',
                        'device.subsystem_maintenance',
                        'device.subsystem_maintenance_parts',
                        'device.subsystem_operation_weightings',
                        'device.subsystem_replacement',

                        'device.control_subsystem_access',
                        'device.control_subsystem_costs',
                        'device.control_subsystem_failure_rates',
                        'device.control_subsystem_inspections',
                        'device.control_subsystem_maintenance',
                        'device.control_subsystem_maintenance_parts',
                        'device.control_subsystem_operation_weightings',
                        'device.control_subsystem_replacement',
                        
                        'component.static_cable',
                        
                        MaskVariable("component.dynamic_cable",
                                     'device.system_type',
                                     ['Tidal Floating', 'Wave Floating']),
                        
                        'component.dry_mate_connectors',
                        'component.wet_mate_connectors',
                        'component.transformers',
                        'component.collection_points',
                        'component.collection_point_cog',
                        'component.collection_point_foundations',
                        
                        "component.foundations_anchor",
                        'component.foundations_anchor_sand',
                        'component.foundations_anchor_soft',
                        "component.foundations_pile",
                 
                        MaskVariable("component.moorings_chain",
                                     'device.system_type',
                                     ['Tidal Floating', 'Wave Floating']),
                        MaskVariable("component.moorings_forerunner",
                                     'device.system_type',
                                     ['Tidal Floating', 'Wave Floating']),
                        MaskVariable("component.moorings_rope",
                                     'device.system_type',
                                     ['Tidal Floating', 'Wave Floating']),
                        MaskVariable("component.moorings_shackle",
                                     'device.system_type',
                                     ['Tidal Floating', 'Wave Floating']),
                        MaskVariable("component.moorings_swivel",
                                     'device.system_type',
                                     ['Tidal Floating', 'Wave Floating']),
                        MaskVariable("component.moorings_rope_stiffness",
                                     'device.system_type',
                                     ['Tidal Floating', 'Wave Floating']),

                        "component.collection_points_NCFR",
                        "component.dry_mate_connectors_NCFR",
                        "component.dynamic_cable_NCFR",
                        "component.static_cable_NCFR",
                        "component.transformers_NCFR",
                        "component.wet_mate_connectors_NCFR",
                        "component.collection_points_CFR",
                        "component.dry_mate_connectors_CFR",
                        "component.dynamic_cable_CFR",
                        "component.static_cable_CFR",
                        "component.transformers_CFR",
                        "component.wet_mate_connectors_CFR",
                        "component.moorings_chain_NCFR",
                        "component.foundations_anchor_NCFR",
                        "component.moorings_forerunner_NCFR",
                        "component.foundations_pile_NCFR",
                        "component.moorings_rope_NCFR",
                        "component.moorings_shackle_NCFR",
                        "component.moorings_swivel_NCFR",
                        "component.moorings_chain_CFR",
                        "component.foundations_anchor_CFR",
                        "component.moorings_forerunner_CFR",
                        "component.foundations_pile_CFR",
                        "component.moorings_rope_CFR",
                        "component.moorings_shackle_CFR",
                        "component.moorings_swivel_CFR",
                        
                        'component.cable_burial',
                        'component.excavating',
                        'component.divers',
                        'component.drilling_rigs',
                        'component.hammer',
                        'component.vibro_driver',
                        'component.rov',
                        'component.mattress_installation',
                        'component.rock_bags_installation',
                        'component.split_pipes_installation',
                        'component.installation_soil_compatibility',
                        'component.equipment_penetration_rates',
                        
                        "component.vehicle_helicopter",
                        "component.vehicle_vessel_ahts",
                        "component.vehicle_vessel_multicat",
                        "component.vehicle_vessel_crane_barge",
                        "component.vehicle_vessel_barge",
                        "component.vehicle_vessel_crane_vessel",
                        "component.vehicle_vessel_csv",
                        "component.vehicle_vessel_ctv",
                        "component.vehicle_vessel_clb",
                        "component.vehicle_vessel_clv",
                        "component.vehicle_vessel_jackup_barge",
                        "component.vehicle_vessel_jackup_vessel",
                        "component.vehicle_vessel_tugboat",
                        
                        'component.ports',
                        'component.port_locations',
                        
                        "component.operations_limit_hs",
                        "component.operations_limit_tp",
                        "component.operations_limit_ws",
                        "component.operations_limit_cs",

                        "project.layout",
                        "project.substation_layout",
                        "project.annual_energy_per_device",
                        "project.mean_power_per_device",
                        
                        "project.network_configuration",
                        'project.landfall_contruction_technique',
                        "project.electrical_network",
                        'project.cable_routes',
                        'project.electrical_component_data',
                        'project.substation_props',
                        
                        MaskVariable('project.umbilical_cable_data',
                                     'device.system_type',
                                     ['Tidal Floating', 'Wave Floating']),
                        MaskVariable('project.umbilical_seabed_connection',
                                     'device.system_type',
                                     ['Tidal Floating', 'Wave Floating']),
                        
                        "project.moorings_foundations_network",
                        "project.moorings_foundations_economics_data",
                        
                        'project.start_date',
                        "project.commissioning_date",
                        'project.commissioning_time',
                        "project.lifetime",
                        'project.cost_contingency',
                        'project.port_percentage_cost',
                        'project.lease_area_entry_point',
                        'project.selected_installation_tool',
                        
                        'project.cable_burial_safety_factors',
                        'project.divers_safety_factors',
                        'project.hammer_safety_factors',
                        'project.port_safety_factors',
                        'project.rov_safety_factors',
                        'project.split_pipe_safety_factors',
                        'project.vessel_safety_factors',

                        'project.fuel_cost_rate',
                        'project.grout_rate',
                        'project.loading_rate',
                        'project.split_pipe_laying_rate',
                        'project.surface_laying_rate',
                        'project.vibro_driver_safety_factors',
                        
                        "project.calendar_based_maintenance",
                        "project.condition_based_maintenance",
                        
                        "project.duration_shift",
                        "project.number_crews_available",
                        "project.number_crews_per_shift",
                        "project.number_shifts_per_day",
                        "project.wage_specialist_day",
                        "project.wage_specialist_night",
                        "project.wage_technician_day",
                        "project.wage_technician_night",
                        "project.workdays_summer",
                        "project.workdays_winter",
                        "project.energy_selling_price",

                        'project.array_cables_operations_weighting',
                        'project.export_cable_operations_weighting',
                        'project.substations_operations_weighting',
                        'project.foundations_operations_weighting',
                        'project.moorings_operations_weighting',
                        
                        MaskVariable('project.umbilical_operations_weighting',
                                     'device.system_type',
                                     ['Tidal Floating', 'Wave Floating']),
                        
                        'project.electrical_onsite_maintenance_requirements',
                        'project.moorings_onsite_maintenance_requirements',
                        'project.electrical_replacement_requirements',
                        'project.moorings_replacement_requirements',
                        
                        'project.electrical_inspections_requirements',
                        'project.moorings_inspections_requirements',
                        
                        'project.electrical_onsite_maintenance_parts',
                        'project.moorings_onsite_maintenance_parts',
                        'project.electrical_replacement_parts',
                        'project.moorings_replacement_parts',

                        "options.operations_inspections",
                        "options.operations_onsite_maintenance",
                        "options.operations_replacements",

                        'options.condition_maintenance_soh',
                        'options.calendar_maintenance_interval',
                        'options.annual_maintenance_start',
                        'options.annual_maintenance_end',
                        
                        'options.subsystem_monitering_costs',

                        'options.spare_cost_multiplier',
                        'options.transit_cost_multiplier',
                        'options.loading_cost_multiplier',
                        
                        "options.curtail_devices",
                        "options.suppress_corrective_maintenance"
                       ]
                 
        return input_list

    @classmethod        
    def declare_outputs(cls):
        
        '''A class method to declare all the output variables provided by
        this interface.
        
        Returns:
          list: List of output identifiers
        
        Example:
          The returned value can be None or a list of identifier strings which 
          appear in the data descriptions. For example::
          
              outputs = ['My:first:variable',
                         'My:third:variable',
                        ]
        '''
        
        output_list = ["project.capex_oandm",
                       "project.lifetime_energy",
                       "project.lifetime_opex",
                       "project.array_downtime",
                       "project.array_availability",
                       "project.downtime_per_device",
                       "project.lifetime_energy_per_device",
                       "project.uptime_series",
                       "project.opex_per_year",
                       "project.energy_per_year",
                       "project.calendar_maintenance_events",
                       "project.condition_maintenance_events",
                       "project.corrective_maintenance_events",
                       "project.operation_journeys"
                       ]
        
        return output_list
        
    @classmethod        
    def declare_optional(cls):
        
        '''A class method to declare all the variables which should be flagged
        as optional.
        
        Returns:
          list: List of optional variable identifiers
        
        Note:
          Currently only inputs marked as optional have any logical effect.
          However, this may change in future releases hence the general
          approach.
        
        Example:
          The returned value can be None or a list of identifier strings which 
          appear in the declare_inputs output. For example::
          
              optional = ['My:first:variable',
                         ]
        '''
        
        options_list = [
                        'device.control_subsystem_access',
                        'device.control_subsystem_costs',
                        'device.control_subsystem_failure_rates',
                        'device.control_subsystem_inspections',
                        'device.control_subsystem_maintenance',
                        'device.control_subsystem_maintenance_parts',
                        'device.control_subsystem_operation_weightings',
                        'device.control_subsystem_replacement',
        
                        'project.electrical_replacement_requirements',
                        'project.moorings_replacement_requirements',
                        'project.electrical_inspections_requirements',
                        'project.moorings_inspections_requirements',
                        'project.electrical_replacement_parts',
                        'project.moorings_replacement_parts',
                        'options.transit_cost_multiplier',
                        'options.loading_cost_multiplier',
                        'options.spare_cost_multiplier',
                        
                        "project.electrical_network",
                        "project.moorings_foundations_network",
                        "component.collection_points_NCFR",
                        "component.dry_mate_connectors_NCFR",
                        "component.dynamic_cable_NCFR",
                        "component.static_cable_NCFR",
                        "component.transformers_NCFR",
                        "component.wet_mate_connectors_NCFR",
                        "component.collection_points_CFR",
                        "component.dry_mate_connectors_CFR",
                        "component.dynamic_cable_CFR",
                        "component.static_cable_CFR",
                        "component.transformers_CFR",
                        "component.wet_mate_connectors_CFR",
                        "component.moorings_chain_NCFR",
                        "component.foundations_anchor_NCFR",
                        "component.moorings_forerunner_NCFR",
                        "component.foundations_pile_NCFR",
                        "component.moorings_rope_NCFR",
                        "component.moorings_shackle_NCFR",
                        "component.moorings_swivel_NCFR",
                        "component.moorings_chain_CFR",
                        "component.foundations_anchor_CFR",
                        "component.moorings_forerunner_CFR",
                        "component.foundations_pile_CFR",
                        "component.moorings_rope_CFR",
                        "component.moorings_shackle_CFR",
                        "component.moorings_swivel_CFR",
                          
                        'component.collection_points',
                        'component.wet_mate_connectors',
                        'component.dry_mate_connectors',
                        'component.static_cable',
                        'component.dynamic_cable',
                        'component.transformers',
                        
                        "component.foundations_anchor",
                        'component.foundations_anchor_sand',
                        'component.foundations_anchor_soft',
                        "component.foundations_pile",
                 
                        "component.moorings_chain",
                        "component.moorings_forerunner",
                        "component.moorings_rope",
                        "component.moorings_shackle",                  
                        "component.moorings_swivel",
                        "component.moorings_rope_stiffness",
                        
                        "component.operations_limit_hs",
                        "component.operations_limit_tp",
                        "component.operations_limit_ws",
                        "component.operations_limit_cs",
                        
                        'project.landfall_contruction_technique',
                        'corridor.layers',
                        'device.bollard_pull',
                        'device.control_subsystem_installation',
                        'project.cable_routes',
                        'project.electrical_component_data',
                        'project.substation_props',
                        'project.umbilical_cable_data',
                        'project.umbilical_seabed_connection',
                        "project.substation_layout",
                        "device.two_stage_assembly",
                        
                        "options.curtail_devices",
                        "options.suppress_corrective_maintenance"

                        ]
                
        return options_list
        
    @classmethod 
    def declare_id_map(self):
        
        '''Declare the mapping for variable identifiers in the data description
        to local names for use in the interface. This helps isolate changes in
        the data description or interface from effecting the other.
        
        Returns:
          dict: Mapping of local to data description variable identifiers 
        
        Example:
          The returned value must be a dictionary containing all the inputs and
          outputs from the data description and a local alias string. For
          example::
          
              id_map = {'var1': 'My:first:variable',
                        'var2': 'My:second:variable',
                        'var3': 'My:third:variable'
                       }
        
        '''
                  
        id_map = {  
            "calendar_based_maintenance": "project.calendar_based_maintenance",
            "condition_based_maintenance":
                "project.condition_based_maintenance",
            "suppress_corrective": "options.suppress_corrective_maintenance",
            "duration_shift": "project.duration_shift",
            "helideck": "farm.helideck",
            "number_crews_available": "project.number_crews_available",
            "number_crews_per_shift": "project.number_crews_per_shift",
            "number_shifts_per_day": "project.number_shifts_per_day",
            "wage_specialist_day": "project.wage_specialist_day",
            "wage_specialist_night": "project.wage_specialist_night",
            "wage_technician_day": "project.wage_technician_day",
            "wage_technician_night": "project.wage_technician_night",
            "workdays_summer": "project.workdays_summer",
            "workdays_winter": "project.workdays_winter",
            "energy_selling_price": "project.energy_selling_price",
            
            "system_type": "device.system_type",
            "network_type": "project.network_configuration",
            "array_layout": "project.layout",
            "bathymetry": "bathymetry.layers",
            "commissioning_date": "project.commissioning_date",
            'annual_maintenance_start': 'options.annual_maintenance_start',
            'annual_maintenance_end': 'options.annual_maintenance_end',
            "mandf_bom": "project.moorings_foundations_economics_data",
            
            "operations_onsite_maintenance":
                "options.operations_onsite_maintenance",
            "operations_replacements": "options.operations_replacements",
            "operations_inspections": "options.operations_inspections",

            'umbilical_operations_weighting':
                'project.umbilical_operations_weighting',
            'array_cables_operations_weighting':
                'project.array_cables_operations_weighting',
            'substations_operations_weighting':
                'project.substations_operations_weighting',
            'export_cable_operations_weighting':
                'project.export_cable_operations_weighting',
            'foundations_operations_weighting':
                'project.foundations_operations_weighting',
            'moorings_operations_weighting':
                'project.moorings_operations_weighting',
                        
            'condition_maintenance_soh': 'options.condition_maintenance_soh',
            'calendar_maintenance_interval':
                'options.calendar_maintenance_interval',
                
            'subsystem_access': 'device.subsystem_access',
            'subsystem_costs': 'device.subsystem_costs',
            'subsystem_failure_rates': 'device.subsystem_failure_rates',
            'subsystem_inspections': 'device.subsystem_inspections',
            'subsystem_maintenance': 'device.subsystem_maintenance',
            'subsystem_maintenance_parts':
                'device.subsystem_maintenance_parts',
            'subsystem_operation_weightings':
                'device.subsystem_operation_weightings',
            'subsystem_replacement': 'device.subsystem_replacement',
            
            'control_subsystem_access': 'device.control_subsystem_access',
            'control_subsystem_costs': 'device.control_subsystem_costs',
            'control_subsystem_failure_rates':
                'device.control_subsystem_failure_rates',
            'control_subsystem_inspections':
                'device.control_subsystem_inspections',
            'control_subsystem_maintenance':
                'device.control_subsystem_maintenance',
            'control_subsystem_maintenance_parts':
                'device.control_subsystem_maintenance_parts',
            'control_subsystem_operation_weightings':
                'device.control_subsystem_operation_weightings',
            'control_subsystem_replacement':
                'device.control_subsystem_replacement',
                
            'electrical_onsite_requirements':
                'project.electrical_onsite_maintenance_requirements',
            'moorings_onsite_requirements':
                'project.moorings_onsite_maintenance_requirements',
            'electrical_replacement_requirements':
                'project.electrical_replacement_requirements',
            'moorings_replacement_requirements':
                'project.moorings_replacement_requirements',
            'electrical_inspections_requirements':
                'project.electrical_inspections_requirements',
            'moorings_inspections_requirements':
                'project.moorings_inspections_requirements',               
            
            'electrical_onsite_parts':
                'project.electrical_onsite_maintenance_parts',
            'moorings_onsite_parts':
                'project.moorings_onsite_maintenance_parts',
            'electrical_replacement_parts':
                'project.electrical_replacement_parts',
            'moorings_replacement_parts': 'project.moorings_replacement_parts',

            'subsystem_monitering_costs': 'options.subsystem_monitering_costs',
            'transit_cost_multiplier': 'options.transit_cost_multiplier',
            'loading_cost_multiplier': 'options.loading_cost_multiplier',
            'spare_cost_multiplier': 'options.spare_cost_multiplier',

            "moor_found_network": "project.moorings_foundations_network",
            "electrical_network": "project.electrical_network",
            "collection_points_NCFR": "component.collection_points_NCFR",
            "dry_mate_connectors_NCFR": "component.dry_mate_connectors_NCFR",
            "dynamic_cable_NCFR": "component.dynamic_cable_NCFR",
            "static_cable_NCFR": "component.static_cable_NCFR",
            "transformers_NCFR": "component.transformers_NCFR",
            "wet_mate_connectors_NCFR": "component.wet_mate_connectors_NCFR",
            "collection_points_CFR": "component.collection_points_CFR",
            "dry_mate_connectors_CFR": "component.dry_mate_connectors_CFR",
            "dynamic_cable_CFR": "component.dynamic_cable_CFR",
            "static_cable_CFR": "component.static_cable_CFR",
            "transformers_CFR": "component.transformers_CFR",
            "wet_mate_connectors_CFR": "component.wet_mate_connectors_CFR",
            "moorings_chain_NCFR": "component.moorings_chain_NCFR",
            "foundations_anchor_NCFR": "component.foundations_anchor_NCFR",
            "moorings_forerunner_NCFR": "component.moorings_forerunner_NCFR",
            "foundations_pile_NCFR": "component.foundations_pile_NCFR",
            "moorings_rope_NCFR": "component.moorings_rope_NCFR",
            "moorings_shackle_NCFR": "component.moorings_shackle_NCFR",
            "moorings_swivel_NCFR": "component.moorings_swivel_NCFR",
            "moorings_chain_CFR": "component.moorings_chain_CFR",
            "foundations_anchor_CFR": "component.foundations_anchor_CFR",
            "moorings_forerunner_CFR": "component.moorings_forerunner_CFR",
            "foundations_pile_CFR": "component.foundations_pile_CFR",
            "moorings_rope_CFR": "component.moorings_rope_CFR",
            "moorings_shackle_CFR": "component.moorings_shackle_CFR",
            "moorings_swivel_CFR": "component.moorings_swivel_CFR",
            
            'assembly_duration': 'device.assembly_duration',
            'bollard_pull': 'device.bollard_pull',
            'cable_burial': 'component.cable_burial',
            'cable_burial_safety_factors':
                'project.cable_burial_safety_factors',
            'cable_routes': 'project.cable_routes',
            'cable_tool': 'project.selected_installation_tool',
            'commission_time': 'project.commissioning_time',
            'connect_duration': 'device.connect_duration',
            'control_system': 'device.control_subsystem_installation',
            'cost_contingency': 'project.cost_contingency',
            'disconnect_duration': 'device.disconnect_duration',
            'divers': 'component.divers',
            'divers_safety_factors': 'project.divers_safety_factors',
            'drilling_rigs': 'component.drilling_rigs',
            'elec_db_cp': 'component.collection_points',
            "collection_point_cog": "component.collection_point_cog",
            "collection_point_foundations": 
                "component.collection_point_foundations",
            'elec_db_dry_mate': 'component.dry_mate_connectors',
            'elec_db_dynamic_cable': 'component.dynamic_cable',
            'elec_db_static_cable': 'component.static_cable',
            'elec_db_transformers': 'component.transformers',
            'elec_db_wet_mate': 'component.wet_mate_connectors',
            'electrical_components': 'project.electrical_component_data',
            'entry_point': 'project.lease_area_entry_point',
            'excavating': 'component.excavating',
            'export': 'corridor.layers',
            'fuel_cost_rate': 'project.fuel_cost_rate',
            'grout_rate': 'project.grout_rate',
            'hammer': 'component.hammer',
            'hammer_safety_factors': 'project.hammer_safety_factors',
            'installation_soil_compatibility':
                'component.installation_soil_compatibility',
            'landfall': 'project.landfall_contruction_technique',
            'lease_utm_zone': 'site.projection',
            'load_out_method': 'device.load_out_method',
            'loading_rate': 'project.loading_rate',
            'mattresses': 'component.mattress_installation',
            'penetration_rates': 'component.equipment_penetration_rates',
            'port_cost': 'project.port_percentage_cost',
            'port_locations': 'component.port_locations',
            'port_safety_factors': 'project.port_safety_factors',
            'ports': 'component.ports',
            'project_start_date': 'project.start_date',
            'rock_bags': 'component.rock_bags_installation',
            'rov': 'component.rov',
            'rov_safety_factors': 'project.rov_safety_factors',
            'split_pipe_laying_rate': 'project.split_pipe_laying_rate',
            'split_pipe_safety_factors': 'project.split_pipe_safety_factors',
            'split_pipes': 'component.split_pipes_installation',
            'sub_device': 'device.subsystem_installation',
            'substations': 'project.substation_props',
            'surface_laying_rate': 'project.surface_laying_rate',
            'system_height': 'device.system_height',
            'system_length': 'device.system_length',
            'system_mass': 'device.system_mass',
            'system_width': 'device.system_width',
            'tidal_series': 'farm.tidal_series_installation',
            'transportation_method': 'device.transportation_method',
            "two_stage_assembly": "device.two_stage_assembly",
            'umbilical_terminations': 'project.umbilical_seabed_connection',
            'umbilicals': 'project.umbilical_cable_data',
            'vessel_safety_factors': 'project.vessel_safety_factors',
            "helicopter": "component.vehicle_helicopter",
            "vessel_ahts": "component.vehicle_vessel_ahts",
            "vessel_multicat": "component.vehicle_vessel_multicat",
            "vessel_crane_barge": "component.vehicle_vessel_crane_barge",
            "vessel_barge": "component.vehicle_vessel_barge",
            "vessel_crane_vessel": "component.vehicle_vessel_crane_vessel",
            "vessel_csv": "component.vehicle_vessel_csv",
            "vessel_ctv": "component.vehicle_vessel_ctv",
            "vessel_clb": "component.vehicle_vessel_clb",
            "vessel_clv": "component.vehicle_vessel_clv",
            "vessel_jackup_barge": "component.vehicle_vessel_jackup_barge",
            "vessel_jackup_vessel": "component.vehicle_vessel_jackup_vessel",
            "vessel_tugboat": "component.vehicle_vessel_tugboat", 
            'vibro_driver': 'component.vibro_driver',
            'vibro_driver_safety_factors':
                'project.vibro_driver_safety_factors',
            'wave_series': 'farm.wave_series_installation',
            'wind_series': 'farm.wind_series_installation',
            
            "annual_energy_per_device": "project.annual_energy_per_device",
            "mean_power_per_device": "project.mean_power_per_device",
            "substation_layout": "project.substation_layout",
            "mission_time": "project.lifetime",
    
            "curtail_devices": "options.curtail_devices",
            
            "capex_oandm": "project.capex_oandm",
            "lifetime_energy": "project.lifetime_energy",
            "lifetime_opex": "project.lifetime_opex",
            "downtime_per_device": "project.downtime_per_device",
            "energy_per_device": "project.lifetime_energy_per_device",
            "array_downtime": "project.array_downtime",
            "array_availability": "project.array_availability",
            "uptime_series": "project.uptime_series",
            "opex_per_year": "project.opex_per_year",
            "energy_per_year": "project.energy_per_year",
            "calendar_maintenance_events":
                "project.calendar_maintenance_events",
            "condition_maintenance_events":
                "project.condition_maintenance_events",
            "corrective_maintenance_events":
                "project.corrective_maintenance_events",
            "journeys": "project.operation_journeys",
            
            "limit_hs": "component.operations_limit_hs",
            "limit_tp": "component.operations_limit_tp",
            "limit_ws": "component.operations_limit_ws",
            "limit_cs": "component.operations_limit_cs",
            
            "foundations_anchor": "component.foundations_anchor",
            'foundations_anchor_sand': 'component.foundations_anchor_sand',
            'foundations_anchor_soft': 'component.foundations_anchor_soft',
            "foundations_pile": "component.foundations_pile",
            "moorings_chain": "component.moorings_chain",
            "moorings_forerunner": "component.moorings_forerunner",
            "moorings_rope": "component.moorings_rope",
            "moorings_shackle": "component.moorings_shackle",
            "moorings_swivel": "component.moorings_swivel",
            "rope_stiffness": "component.moorings_rope_stiffness",
            
            }
                  
        return id_map
                 
    def connect(self, debug_entry=False,
                      export_data=True):
        
        '''The connect method is used to execute the external program and 
        populate the interface data store with values.
        
        Note:
          Collecting data from the interface for use in the external program
          can be accessed using self.data.my_input_variable. To put new values
          into the interface once the program has run we set
          self.data.my_output_variable = value
        
        '''
        
#        Farm_OM (dict): This parameter records the O&M general information for 
#        the farm as whole keys.
#            
#            calendar_based_maintenance (bool) [-]:
#                User input if one wants to consider calendar based maintenance
#            condition_based_maintenance (bool) [-]:
#                User input if one wants to consider condition based
#                maintenance                             
#            corrective_maintenance (bool) [-]:
#                User input if one wants to consider corrective maintenance
#            duration_shift (int) [h]: Duration of a shift
#            helideck (str or bool -> logistic) [-]:
#                If there is helideck available or not?    
#            number_crews_available (int) [-]: Number of available crews
#            number_crews_per_shift (int) [-]: Number of crews per shift
#            number_shifts_per_day (int) [-]: Number of shifts per day                           
#            wage_specialist_day (float) [€/h]:
#                Wage for specialists crew at daytime e.g. diver
#            wage_specialist_night (float) [€/h]:
#                Wage for specialists crew at night time e.g. diver
#            wage_technician_day (float) [€/h]: Wage for technicians at daytime
#            wage_technician_night (float) [€/h]:
#                Wage for technicians at night time                
#            workdays_summer (int) [-]: Working Days per Week during summer
#            workdays_winter (int) [-]: Working Days per Week during winter

        # Suppress corrective maintenance
        corrective_maintenance = True
        
        if self.data.suppress_corrective is not None:
            corrective_maintenance = not self.data.suppress_corrective
        
        farm_OM = {
            "calendar_based_maintenance":
                self.data.calendar_based_maintenance,
            "condition_based_maintenance":
                self.data.condition_based_maintenance,
            "corrective_maintenance": corrective_maintenance,
            "duration_shift": self.data.duration_shift,
            "helideck": self.data.helideck,
            "number_crews_available": self.data.number_crews_available,
            "number_crews_per_shift": self.data.number_crews_per_shift,
            "number_shifts_per_day": self.data.number_shifts_per_day,
            "wage_specialist_day": self.data.wage_specialist_day,
            "wage_specialist_night": self.data.wage_specialist_night,
            "wage_technician_day": self.data.wage_technician_day,
            "wage_technician_night": self.data.wage_technician_night,
            "workdays_summer": self.data.workdays_summer,
            "workdays_winter": self.data.workdays_winter,
            "energy_selling_price": self.data.energy_selling_price
            }
        
#        Component (Pandas DataFrame): This table stores information related to
#        the components. A component is any physical object required during the
#        operation of the farm.
#        
#        Please note that each defined component will be a column in Pandas
#        DataFrame table “Component”
#            keys:
#                component_id (str) [-]: Id of components   
#                component_type (str) [-]: Type of components
#                component_subtype: (str) [-]: sub type of components  
#                failure_rate (float) [1/year]: Failure rate of the components
#                number_failure_modes (int) [-]: Number of failure modes for
#                    this component
#                start_date_calendar_based_maintenance (datetime) [-]:
#                    Start date of calendar-based maintenance for each year
#                end_date_calendar_based_maintenance	 (datetime)	[-]:
#                    End date of calendar-based maintenance for each year
#                interval_calendar_based_maintenance	int (year) [-]:
#                    Interval of calendar-based maintenance
#                start_date_condition_based_maintenance (datetime) [-]:
#                    Start date of condition-based maintenance for each year
#                end_date_condition_based_maintenance (datetime) [-]:
#                    End date of condition-based maintenance
#                soh_threshold (float) [-]: This parameter belongs to condition
#                    based strategy
#                is_floating (bool) [-]: Component is floating and can be towed
#                    to port
#
#        Failure_Mode (Pandas DataFrame): This table stores information related
#        to the failure modes of components
#        Please note that each defined failure mode will be a column in Pandas
#        DataFrame table “Failure_Mode”
#            keys:
#                component_id (str) [-]          : Id of component
#                fm_id (str) [-]                 : Id of failure mode 
#                mode_probability (float) [%]    : Probability of occurrence of each failure modes
#                spare_mass (float) [kg]         : Mass of the spare parts
#                spare_height	 (float)	[m]     : Height of the spare parts
#                spare_width	int (float) [m]    : Width of the spare parts
#                spare_length (float) [m]        : Length of the spare parts
#                cost_spare (float) [€]          : Cost of the spare parts
#                cost_spare_transit	(float) [€]   : Cost of the transport of the spare parts
#                cost_spare_loading	(float) [€]   : Cost of the loading of the spare parts
#                lead_time_spare	(bool) [days] : Lead time for the spare parts
#        
#        Repair_Action (Pandas DataFrame): This table stores information
#        related to the repair actions required for each failure modes
#        Please note that each defined repair action will be a column in Pandas
#        DataFrame table “Repair_Action”:
#            keys:
#                component_id (str) [-]              : Id of component
#                fm_id (str) [-]                     : Id of failure mode                 
#                duration_maintenance (float) [h]    : Duration of time required on site for maintenance
#                duration_accessibility (float) [h]  : Duration of time required on site to access the component or sub-systems to be repaired or replaced
#                interruptable (bool) [-]            : Is the failure mode type interruptable or not                              
#                delay_crew (float) [h]              : duration of time before the crew is ready
#                delay_organisation (float) [h]      : duration of time before anything else is ready
#                delay_spare	(float) [h]            : duration of time before the spare parts are ready
#                number_technicians (int) [-]        : Number of technicians required to do the O&M
#                number_specialists (int) [-]        : Number of specialists required to do the O&M
#                wave_height_max_acc (float) [m]     : wave height max for operational limit conditions during the accessibility
#                wave_periode_max_acc (float) [s]    : wave period max for operational limit conditions during the accessibility
#                wind_speed_max_acc (float) [m/s]    : wind speed max for operational limit conditions during the accessibility
#                current_speed_max_acc (float) [m/s] : current speed max for operational limit conditions during the accessibility                
#                wave_height_max_om (float) [m]      : wave height max for operational limit conditions during the maintenance action
#                wave_periode_max_om (float) [s]     : wave period max for operational limit conditions during the maintenance action
#                wind_speed_max_om	 (float) [m/s]    : wind speed max for operational limit conditions during the maintenance action
#                current_speed_max_om (float) [m/s]  : current speed max for operational limit conditions during the maintenance action               
#                requires_lifiting	 (bool) [-]       : Is lifting required?
#                requires_divers (bool) [-]          : Are divers required?
#                requires_towing (bool) [-]          : Is towing required?
#            
#         
#        Inspection (Pandas DataFrame): This table stores information related
#        to the inspections required for each failure modes
#        Please note that each defined inspection will be a column in Pandas
#        DataFrame table “Repair_Action”:
#            keys:                    
#                component_id (str) [-]              : Id of component
#                fm_id (str) [-]                     : Id of failure mode        
#                duration_inspection (float) [h]     : Duration of time required on site for inspection
#                duration_accessibility (float) [h]  : Duration of time required on site to access the component or sub-systems to be repaired or replaced
#                delay_crew (float) [h]              : duration of time before the crew is ready
#                delay_organisation (float) [h]      : duration of time before anything else is ready             
#                number_technicians (int) [-]        : Number of technicians required to do the O&M
#                number_specialists (int) [-]        : Number of specialists required to do the O&M
#                wave_height_max_acc (float) [m]     : Wave height max for operational limit conditions during the accessibility
#                wave_periode_max_acc (float) [s]    : Wave period max for operational limit conditions during the accessibility
#                wind_speed_max_acc (float) [m/s]    : Wind speed max for operational limit conditions during the accessibility
#                current_speed_max_acc (float) [m/s] : Current speed max for operational limit conditions during the accessibility
#                wave_height_max_om (float) [m]      : Wave height max for operational limit conditions during the maintenance action
#                wave_periode_max_om (float) [s]     : Wave period max for operational limit conditions during the maintenance action
#                wind_speed_max_om	 (float) [m/s]    : Wind speed max for operational limit conditions during the maintenance action
#                current_speed_max_om (float) [m/s]  : Current speed max for operational limit conditions during the maintenance action
#                requires_lifiting	 (bool) [-]       : Is lifting required?
#                requires_divers (bool) [-]          : Are divers required?

        if self.data.electrical_network is not None:
            
            none_check = [x is None for x in
                                      [self.data.elec_db_static_cable,
                                       self.data.elec_db_wet_mate,
                                       self.data.elec_db_dry_mate,
                                       self.data.elec_db_transformers,
                                       self.data.elec_db_cp,
                                       self.data.collection_point_cog,
                                       self.data.collection_point_foundations]]
            
            if "floating" in self.data.system_type.lower():
                
                none_check += [self.data.elec_db_dynamic_cable is None]
                
            if any(none_check):
                
                errMsg = ("Electrical component databases must be defined if "
                          "providing an electrical network to analyse")
                raise ValueError(errMsg)

            elec_database = ElectricalInterface.get_component_database(
                                        self.data.system_type,
                                        self.data.elec_db_static_cable,
                                        self.data.elec_db_dynamic_cable,
                                        self.data.elec_db_wet_mate,
                                        self.data.elec_db_dry_mate,
                                        self.data.elec_db_transformers,
                                        self.data.elec_db_cp,
                                        self.data.collection_point_cog,
                                        self.data.collection_point_foundations)
            
        if self.data.moor_found_network is not None:
            
            none_check = [x is None for x in
                                          [self.data.foundations_anchor,
                                           self.data.foundations_anchor_sand,
                                           self.data.foundations_anchor_soft,
                                           self.data.foundations_pile]]
            
            if "floating" in self.data.system_type.lower():
                
                float_check = [x is None for x in
                                           [self.data.moorings_chain,
                                            self.data.moorings_forerunner,
                                            self.data.moorings_rope,
                                            self.data.rope_stiffness,
                                            self.data.moorings_shackle,
                                            self.data.moorings_swivel,
                                            self.data.elec_db_dynamic_cable]]
                
                none_check += float_check
                
            if any(none_check):
                
                errMsg = ("Moorings and foundations component databases must "
                          "be defined if providing a moorings and foundations "
                          "network to analyse")
                raise ValueError(errMsg)
        
            mandf_database = MooringsInterface.get_all_components(
                                            self.data.system_type,
                                            self.data.foundations_anchor,
                                            self.data.foundations_anchor_sand,
                                            self.data.foundations_anchor_soft,
                                            self.data.foundations_pile,
                                            self.data.moorings_chain,
                                            self.data.moorings_forerunner,
                                            self.data.moorings_rope,
                                            self.data.rope_stiffness,
                                            self.data.moorings_shackle,
                                            self.data.moorings_swivel,
                                            self.data.elec_db_dynamic_cable)
        
        # Modify the replacement and replacement parts table
        limits_cols = ['Max Hs',
                       'Max Tp',
                       'Max Wind Velocity',
                       'Max Current Velocity']
                
        replacement_limits = self.data.sub_device[limits_cols]
        
        subsystem_replacement = pd.concat([self.data.subsystem_replacement, 
                                           replacement_limits],
                                          axis=1)
        
        parts_cols = ["Length", "Width", "Height", "Dry Mass"]
        parts_map = {"Length": "Spare Parts Max Length",
                     "Width": "Spare Parts Max Width",
                     "Height": "Spare Parts Max Height",
                     "Dry Mass": "Spare Parts Mass"}
                
        replacement_parts = self.data.sub_device[parts_cols]
        replacement_parts = replacement_parts.rename(columns=parts_map)
        
        control_replacement = None        
        control_replacement_parts = None
        
        if self.data.control_system is not None:
            
            control_replacement_limits = self.data.control_system[limits_cols]
            
            control_replacement = pd.concat(
                                    [self.data.control_subsystem_replacement, 
                                     control_replacement_limits],
                                    axis=1)
    
            control_replacement_parts = self.data.control_system[parts_cols]
            control_replacement_parts = control_replacement_parts.rename(
                                                            columns=parts_map)

        (component_df,
         failure_mode_df,
         repair_action_df,
         inspection_df) = get_input_tables(
                            self.data.system_type,
                            self.data.network_type,
                            self.data.array_layout,
                            self.data.bathymetry,
                            self.data.commissioning_date,
                            self.data.annual_maintenance_start,
                            self.data.annual_maintenance_end,
                            self.data.electrical_network,
                            self.data.moor_found_network,
                            self.data.mandf_bom,
                            self.data.electrical_components,
                            elec_database,
                            mandf_database,
                            self.data.operations_onsite_maintenance,
                            self.data.operations_replacements,
                            self.data.operations_inspections,
                            self.data.subsystem_access,
                            self.data.subsystem_costs,
                            self.data.subsystem_failure_rates,
                            self.data.subsystem_inspections,
                            self.data.subsystem_maintenance,
                            self.data.subsystem_maintenance_parts,
                            self.data.subsystem_operation_weightings,
                            subsystem_replacement,
                            replacement_parts,
                            self.data.control_subsystem_access,
                            self.data.control_subsystem_costs,
                            self.data.control_subsystem_failure_rates,
                            self.data.control_subsystem_inspections,
                            self.data.control_subsystem_maintenance,
                            self.data.control_subsystem_maintenance_parts,
                            self.data.control_subsystem_operation_weightings,
                            control_replacement,
                            control_replacement_parts,
                            self.data.umbilical_operations_weighting,
                            self.data.array_cables_operations_weighting,
                            self.data.substations_operations_weighting,
                            self.data.export_cable_operations_weighting,
                            self.data.foundations_operations_weighting,
                            self.data.moorings_operations_weighting,
                            self.data.calendar_maintenance_interval,
                            self.data.condition_maintenance_soh,
                            self.data.electrical_onsite_requirements,
                            self.data.moorings_onsite_requirements,
                            self.data.electrical_replacement_requirements,
                            self.data.moorings_replacement_requirements,
                            self.data.electrical_inspections_requirements,
                            self.data.moorings_inspections_requirements,
                            self.data.electrical_onsite_parts,
                            self.data.moorings_onsite_parts,
                            self.data.electrical_replacement_parts,
                            self.data.moorings_replacement_parts,
                            self.data.subsystem_monitering_costs,
                            self.data.spare_cost_multiplier,
                            self.data.transit_cost_multiplier,
                            self.data.loading_cost_multiplier)
        
#        RAM_Param (dict): This parameter records the information for talking
#                          to RAM module
#            keys:         
#        systype (str) [-]: system type: options:    'tidefloat', 
#                                                    'tidefixed', 
#                                                    'wavefloat', 
#                                                    'wavefixed'
#        eleclayout (str) [-]: electrical system architecture: options:   'radial'
#                                                                         'singlesidedstring'
#                                                                         'doublesidedstring'
#                                                                         'multiplehubs'
#        elechierdict (dict): array-level electrical system hierarchy: keys: array: export cable: export cable components (list) [-],
#                                                                                   substation: substation components (list) [-],
#                                                                                   layout: device layout
#                                                                            deviceXXX: elec sub-system
#        moorhiereg (dict): array-level mooring and foundation hierarchy: keys: array: substation foundation: substation foundation components (list) [-]
#                                                                                      deviceXXX:  umbilical:   umbilical type (str) [-],
#                                                                                                  foundation: foundation components (list) [-],
#                                                                                                  mooring system: mooring components (list) [-]
#
#        RAM_Param['systype']
#        RAM_Param['eleclayout']
#        RAM_Param['elechierdict']
#        RAM_Param['elecbomeg']
#        RAM_Param['moorhiereg']
#        RAM_Param['moorbomeg']
#        RAM_Param['userhiereg']
#        RAM_Param['userbomeg']
#        RAM_Param['db']

        system_type_map = {"Tidal Floating" : "tidefloat",
                           "Tidal Fixed" : "tidefixed",
                           "Wave Floating" : "wavefloat",
                           "Wave Fixed" : "wavefixed"
                           }
        system_type = system_type_map[self.data.system_type]

        reliability_input_dict = \
            ReliabilityInterface.get_input_dict(self.data,
                                                self.data.network_type)
        
        RAM_param = {}
        RAM_param['systype'] = system_type

        if reliability_input_dict is None:

            RAM_param['eleclayout'] = None
            RAM_param['elechierdict'] = None
            RAM_param['elecbomeg'] = None
            RAM_param['moorhiereg'] = None
            RAM_param['moorbomeg'] = None

            compdict = {} 

        else:

            RAM_param['eleclayout'] = \
                            reliability_input_dict["network_configuration"]
            RAM_param['elechierdict'] = \
                            reliability_input_dict["electrical_network_hier"]
            RAM_param['elecbomeg'] = \
                            reliability_input_dict["electrical_network_bom"]
            RAM_param['moorhiereg'] = \
                            reliability_input_dict["moor_found_network_hier"]
            RAM_param['moorbomeg'] = \
                            reliability_input_dict["moor_found_network_bom"]

            compdict = reliability_input_dict["compdict"]

        # Manufacture the user network for the device subsytems:
        subsytem_comps = ['hydro001',
                          'pto001',
                          'support001']
        
        if self.data.control_system is not None:
            subsytem_comps.insert(2,'control001')
            
        user_hierarchy, user_bom = get_user_network(subsytem_comps,
                                                    self.data.array_layout)
        
        user_compdict = get_user_compdict(subsytem_comps,
                                          self.data.subsystem_failure_rates)
        compdict.update(user_compdict)
        
        RAM_param['userhiereg'] = user_hierarchy
        RAM_param['userbomeg'] = user_bom
        RAM_param['db'] = compdict

#        Logistic_Param (dict): This parameter records the information for
#                               talking to logistic module
#            keys:
#                 'cable_route',
#                 'collection_point',
#                 'connectors',
#                 'device',
#                 'dynamic_cable',
#                 'entry_point',
#                 'eq_sf',
#                 'equipments',
#                 'external_protection',
#                 'landfall',
#                 'laying_rates',
#                 'layout',
#                 'metocean',
#                 'other_rates',
#                 'penet_rates',
#                 'phase_order',
#                 'port_sf',
#                 'ports',
#                 'schedule_OLC',
#                 'site',
#                 'static_cable',
#                 'sub_device',
#                 'topology',
#                 'vessel_sf',
#                 'vessels'

        # check that proj4 string is correctly formatted
        if not all(x in self.data.lease_utm_zone for x in ['utm', 'zone']): 

            errStr = ("Site projection not correctly defined. Must contain " +
                      "both 'utm' and 'zone' keys")

            raise ValueError(errStr)

        else:

            # could not get re search to work so using crude method between
            # two strings
            utm_zone = self.data.lease_utm_zone           
            zone = \
                utm_zone[utm_zone.find("zone=")+5:\
                         utm_zone.find(" +", utm_zone.find("zone=")+1)]

            zone = zone + ' U' # prepare for module

        installation_input_dict = InstallationInterface.get_input_dict(
                                    self.data,
                                    self.data.bathymetry,
                                    self.data.system_type,
                                    self.data.array_layout,
                                    self.data.electrical_network,
                                    self.data.moor_found_network,
                                    zone)
        
#        entry_point = self.data.entry_point
#        entry_point_coords = list(entry_point.coords[0])
#        entry_point_coords.append(zone)

        logistic_param = {
            'cable_route': installation_input_dict['cable_route_df'],
            'collection_point': installation_input_dict['collection_point_df'],
            'connectors': installation_input_dict['connectors_df'],
            'device': installation_input_dict['device_df'],
            'dynamic_cable': installation_input_dict['dynamic_cable_df'],
            'entry_point': installation_input_dict['entry_point_df'],
            'eq_sf': installation_input_dict['equipment_safety_factor_df'],
            'equipments': installation_input_dict['equipment'],
            'external_protection':
                installation_input_dict['external_protection_df'],
            'landfall': installation_input_dict['landfall_df'],
            'laying_rates': installation_input_dict['laying_rate_df'],
            'layout': installation_input_dict['layout_df'],
            'metocean': installation_input_dict['metocean_df'],
            'other_rates': installation_input_dict['other_rates_df'],
            'penet_rates': installation_input_dict['penetration_rate_df'],
            'phase_order': installation_input_dict['phase_order_df'],
            'port_sf': installation_input_dict['port_safety_factor_df'],
            'ports': installation_input_dict['ports_df'],
            'schedule_OLC': installation_input_dict['schedule_OLC'],
            'site': installation_input_dict['whole_area'],
            'static_cable': installation_input_dict['static_cable_df'],
            'sub_device': installation_input_dict['sub_device_df'],
            'topology': installation_input_dict['topology'],
            'vessel_sf': installation_input_dict['vessel_safety_factor_df'],
            'vessels': installation_input_dict['vessels_df']
            }

#        Simu_Param (dict): This parameter records the general information
#                           concerning the simulation
#            keys:          
#                Nbodies (int) [-]                                  : Number of devices 
#                annual_Energy_Production_perD (numpy.ndarray) [Wh] : Annual energy production of each device on the array. The dimension of the array is Nbodies x 1 (WP2)
#                arrayInfoLogistic (DataFrame) [-]                   : Information about component_id, depth, x_coord, y_coord, zone, bathymetry, soil type
#                missionTime (float) [year]                          : Simulation time             
#                power_prod_perD (numpy.ndarray) [W]                 : Mean power production per device. The dimension of the array is Nbodies x 1 (WP2) 
#                startOperationDate (datetime) [-]                   : Date of simulation start

#                 	Component1 	Component2 	Component3 	Component4 	Component5
#        Component_ID 	device001 	device002 	device003 	Export Cable001 	Substation001
#        depth 	19 	14 	20 	20 	20
#        x coord 	367341 	367586 	367445 	367445 	367445
#        y coord 	6128092 	6128977 	6127445 	6127445 	6127445
#        zone 	31 U 	30 U 	30 U 	30 U 	30 U
#        Bathymetry 	81 	104 	103 	103 	103
#        Soil type 	MS 	SC 	SC 	SC 	SC

        # Order outputs by device number
        dev_ids = self.data.array_layout.keys()
        dev_ids.sort()
        
        AEP_per_device = [self.data.annual_energy_per_device[x] * 1e6
                                                          for x in dev_ids]
        mean_power_per_device = [self.data.mean_power_per_device[x] * 1e6
                                                          for x in dev_ids]
                                                          
        # Build "arrayInfoLogistic" table
        array_df = pd.DataFrame()
        
        for device_id in dev_ids:
            
            dev_series = pd.Series()
            dev_series["Component_ID"] = device_id
            
            position = self.data.array_layout[device_id]
            dev_series['x coord'] = position.coords[0][0]
            dev_series['y coord'] = position.coords[0][1]

            point_bathy = get_point_depth(self.data.bathymetry, position)
            
            if "floating" in system_type.lower():
                depth = 0.
            else:
                depth = -point_bathy
                
            dev_series['depth'] = depth
            dev_series['Bathymetry'] = -point_bathy
            dev_series['zone'] = zone
            dev_series["Soil type"] = None

            num_cols = array_df.shape[1]
            dev_series = dev_series.rename(num_cols)
            array_df = pd.concat([array_df, dev_series],
                                  axis=1)
            
        # If we have the electrical network then add the export cable
        # and the substation at the same locaton.        
        if self.data.electrical_network is not None:
            
            if self.data.substation_layout is None:
                
                errStr = ("The substation layout must be provided alongside "
                          "the electrical network")
                raise RuntimeError(errStr)
                
            array_series = pd.Series()
            array_series["Component_ID"] = "Substation001"
            array_series['depth'] = 0.
            array_series['zone'] = zone
            array_series["Soil type"] = None
                            
            array_pos = self.data.substation_layout['array']
            array_series['x coord'] = array_pos.coords[0][0]
            array_series['y coord'] = array_pos.coords[0][1]

            point_bathy = get_point_depth(self.data.bathymetry, array_pos)
            array_series['Bathymetry'] = -point_bathy

            num_cols = array_df.shape[1]
            array_series = array_series.rename(num_cols)
            array_df = pd.concat([array_df, array_series],
                                      axis=1)
                        
            if self.data.network_type == 'Star':
                                                
                self.data.substation_layout.pop('array')
                                
                for (subhub_id, 
                     array_pos) in self.data.substation_layout.iteritems():
                                                            
                    array_series['x coord'] = array_pos.coords[0][0]
                    array_series['y coord'] = array_pos.coords[0][1]
        
                    point_bathy = get_point_depth(self.data.bathymetry,
                                                  array_pos)
                    
                    array_series["Component_ID"] = subhub_id
                    array_series['Bathymetry'] = -point_bathy

                    num_cols = array_df.shape[1]
                    array_series = array_series.rename(num_cols)
                    array_df = pd.concat([array_df, array_series],
                                          axis=1)
            
            array_series["Component_ID"] = "Export Cable001"
            array_series['depth'] = -point_bathy
            
            num_cols = array_df.shape[1]
            array_series = array_series.rename(num_cols)
            array_df = pd.concat([array_df, array_series],
                                  axis=1)
        
        simu_param = {"Nbodies": len(dev_ids),
                      "annual_Energy_Production_perD": AEP_per_device,
                      "arrayInfoLogistic": array_df,
                      "missionTime":  self.data.mission_time,
                      "power_prod_perD": mean_power_per_device,
                      "startOperationDate": self.data.commissioning_date}
                      
                      
#        Control_Param (dict): This parameter records the O&M module control from GUI (to be extended in future)
#            keys:          
#                whichOptim (list) [bool]           : Which O&M should be optimised [Unplanned corrective maintenance, Condition based maintenance, Calendar based maintenance]
#                checkNoSolution (bool) [-]         : see below
#                checkNoSolutionWP6Files (bool) [-] : see below             
#                integrateSelectPort (bool) [-]     : see below)                 
#          
#                ###############################################################################
#                ###############################################################################
#                ###############################################################################
#                # Some of the function developed by logistic takes some times for running. 
#                # With the following flags is possible to control the call of such functions.
#                
#                # Control_Param['integrateSelectPort'] is True  -> call OM_PortSelection
#                # Control_Param['integrateSelectPort'] is False -> do not call OM_PortSelection, set constant values for port parameters
#                Control_Param['integrateSelectPort'] = False 
#                
#                # Control_Param['checkNoSolution'] is True  -> check the feasibility of logistic solution before the simulation 
#                # Control_Param['checkNoSolution'] is False -> do not check the feasibility of logistic solution before the simulation
#                Control_Param['checkNoSolution'] = False 
#                 
#                ###############################################################################
#                ###############################################################################
#                ###############################################################################   
                                  
        if self.data.curtail_devices is not None:
            ignoreWeatherWindow = not self.data.curtail_devices
        else:
            ignoreWeatherWindow = False
            
        control_param = {"whichOptim": None,
                         "ignoreWeatherWindow": ignoreWeatherWindow,
                         "checkNoSolution" : True,
                         'dtocean_logistics_PRINT_FLAG': False,
                         'dtocean_maintenance_PRINT_FLAG': False,
                         'dtocean_maintenance_TEST_FLAG': False
                         }
                         
        inputOMPtr = inputOM(farm_OM,
                             component_df,
                             failure_mode_df,
                             repair_action_df,
                             inspection_df,
                             RAM_param,
                             logistic_param,
                             simu_param,
                             control_param)
        
        if export_data:
            
            userdir = UserDataDirectory("dtocean_core", "DTOcean", "config")
                    
            if userdir.isfile("files.ini"):
                configdir = userdir
            else:
                configdir = ObjDirectory("dtocean_core", "config")
            
            files_ini = ReadINI(configdir, "files.ini")
            files_config = files_ini.get_config()
            
            appdir_path = userdir.get_path("..")
            debug_folder = files_config["debug"]["path"]
            debug_path = os.path.join(appdir_path, debug_folder)
            debugdir = Directory(debug_path)
            debugdir.makedir()

            pkl_path = debugdir.get_path("oandm_inputs.pkl")
            pickle.dump(inputOMPtr, open(pkl_path, "wb"))
            
        # Call WP6 optimiser
        ptrOptim = LCOE_Optimiser(inputOMPtr)
        
        if debug_entry: return
        
        # Run the module
        outputWP6 = ptrOptim()
        
        error_df = outputWP6['error [-]']
        
        if error_df['error_ID [-]'][0] == 'NoSolutionsFound':
            
            dfStr = error_df.to_string(line_width=79, justify="left")
            logStr = "Errors detected:\n{}".format(dfStr)
            
            module_logger.critical(logStr)
            
            errStr = ('Problem with feasibility of logistic solution: '
                      'please see logging for more details')
            raise RuntimeError(errStr)
        
        # Reset check no solution
        inputOMPtr._inputOM__Control_Param['checkNoSolution'] = False

        # Call WP6 optimiser
        ptrOptim = LCOE_Optimiser(inputOMPtr)
                
        # Run the module
        outputWP6 = ptrOptim()
        
        if export_data:
            
            pkl_path = debugdir.get_path("oandm_outputs.pkl")
            pickle.dump(outputWP6, open(pkl_path, "wb"))
        
        self.data.capex_oandm = outputWP6["CapexOfArray [Euro]"]
        
        # Calculate operations costs per year
        start_year = self.data.project_start_date.year
        commisioning_year = self.data.commissioning_date.year
        end_year = commisioning_year + self.data.mission_time
        
        years = range(start_year, end_year + 1)
        n_years = len(years)
        year_idxs = range(n_years)
        year_map = {year: idx for year, idx in zip(years, year_idxs)}
        
        eco_dict = {"Year": year_idxs,
                    "Cost": [0] * n_years}
                
        eco_df = pd.DataFrame(eco_dict)
        eco_df = eco_df.set_index("Year")
                
        for event_df in outputWP6['eventTables [-]'].itervalues():
            
            if event_df.isnull().values.all(): continue
        
            event_df = event_df.dropna()
            event_df = event_df.set_index("repairActionDate [-]")
            event_df.index = pd.to_datetime(event_df.index)
            
            event_df = event_df[["ComponentType [-]",
                                 "costLogistic [Euro]",
                                 "costOM_Labor [Euro]",
                                 "costOM_Spare [Euro]"]]

            # Prepare a dataframe for each component type
            grouped = event_df.groupby("ComponentType [-]")
            group_dict = {}
            
            for name, comp_df in grouped:
                    
                comp_df = comp_df.drop("ComponentType [-]", 1)
                comp_df["Total Cost"] = \
                                comp_df[["costLogistic [Euro]",
                                         "costOM_Labor [Euro]",
                                         "costOM_Spare [Euro]"]].sum(axis=1)
                comp_df = comp_df.convert_objects(convert_numeric=True)
                comp_df = comp_df.resample("A").sum()
                comp_df.index = comp_df.index.map(lambda x: x.year)
                comp_df = comp_df.dropna()
                                
                group_dict[name] = comp_df

            # Record energy and costs for each year
            year_costs = []
            
            for year in years:
    
                year_cost = 0.  
            
                for name, comp_df in group_dict.iteritems():
                    
                    if year not in comp_df.index: continue
                        
                    year_series = comp_df.loc[year]
                    year_cost += year_series["Total Cost"]
                                      
                year_costs.append(year_cost)
                
            year_dict = {"Year": year_idxs,
                         "Cost": year_costs}
    
            year_df = pd.DataFrame(year_dict)
            year_df = year_df.set_index("Year")
            
            eco_df = eco_df.add(year_df)
            
        self.data.opex_per_year = eco_df.reset_index()
        self.data.lifetime_opex = eco_df.sum()[0]
        
        # Calculate device uptime per year
        end_date = self.data.commissioning_date + relativedelta(
                                                years=+self.data.mission_time)
        
        uptime_dict = {"Date": [self.data.commissioning_date, end_date]}
        
        for device_id in dev_ids:
            uptime_dict[device_id] = [1, 1]
            
        uptime_df = pd.DataFrame(uptime_dict)
        uptime_df = uptime_df.set_index("Date")
        uptime_df = uptime_df.resample("H").pad()
        max_uptime = len(uptime_df)
        
        for event_df in outputWP6['eventTables [-]'].itervalues():
                        
            repair_df = event_df[["repairActionRequestDate [-]",
                                  "repairActionDate [-]",
                                  "downtimeDuration [Hour]",
                                  'downtimeDeviceList [-]']]
            repair_df["repairActionRequestDate [-]"] = pd.to_datetime(
                                    repair_df["repairActionRequestDate [-]"])
            repair_df["repairActionDate [-]"] = pd.to_datetime(
                                    repair_df["repairActionDate [-]"])
            
            for _, row in repair_df.iterrows():
                
                isnull = pd.isnull(row).all()
                
                if isnull: continue
                                            
                for device_id in row['downtimeDeviceList [-]']:
                
                    downtime_start = row["repairActionDate [-]"]
                    downtime = row["downtimeDuration [Hour]"]
                    downtime_end = downtime_start + \
                                         datetime.timedelta(hours=downtime)
                                         
                    # Avoid zero downtime events
                    if downtime_start == downtime_end: continue
                    
                    action_dict = {"Date": [downtime_start,
                                            downtime_end]}
                    action_dict[device_id] = [0, 0]
        
                    action_df = pd.DataFrame(action_dict)
                    action_df = action_df.set_index("Date")
                                                            
                    action_df = action_df.resample("H").pad()
                    uptime_df.update(action_df)
                                    
        array_uptime_series = uptime_df.max(1)
        array_uptime = array_uptime_series.sum()
        
        array_downtime = max_uptime - array_uptime
        array_availability = 1 - array_downtime / max_uptime
        
        device_downtime_series = max_uptime - uptime_df.sum()
        device_downtime_dict = {device_id: device_downtime_series[device_id]
                                                    for device_id in dev_ids}        
        
        self.data.array_downtime = array_downtime
        self.data.downtime_per_device = device_downtime_dict
        self.data.array_availability = array_availability
        self.data.uptime_series = array_uptime_series
        
        uptime_df = uptime_df.resample("A").sum()
        uptime_df.index = uptime_df.index.map(lambda x: x.year)
        
        # Energy calculation
        dev_energy_dict = {device_id: [] for device_id in dev_ids}
        
        for year, row in uptime_df.iterrows():
            
            for device_id in dev_ids:
        
                year_energy = row[device_id] * \
                                self.data.mean_power_per_device[device_id]
                dev_energy_dict[device_id].append(year_energy)
                
        dev_energy_dict["Year"] = list(uptime_df.index.values)
        dev_energy_df = pd.DataFrame(dev_energy_dict)
        dev_energy_df = dev_energy_df.set_index("Year")
                        
        dev_energy_df["Energy"] = dev_energy_df.sum(1)
        dev_energy_series = dev_energy_df.sum()
        dev_energy_df = dev_energy_df.reset_index()
        
        dev_energy_dict = {device_id: dev_energy_series[device_id] for
                                                        device_id in dev_ids}
        
        array_energy_df = dev_energy_df[["Year", "Energy"]]
        array_energy_df["Year"] = array_energy_df["Year"].replace(year_map)
        array_energy_df = array_energy_df.set_index("Year")
        
        base_energy_dict = {"Year": year_map.values(),
                            "Energy": [0] * len(year_map)}
        base_energy_df = pd.DataFrame(base_energy_dict)
        base_energy_df = base_energy_df.set_index("Year")
        
        base_energy_df.update(array_energy_df)
        base_energy_df = base_energy_df.reset_index()
                
        base_energy_df["Year"] = base_energy_df["Year"].astype(int)
        base_energy_df = base_energy_df.sort_values("Year")
        
        self.data.lifetime_energy = dev_energy_series["Energy"]
        self.data.energy_per_device = dev_energy_dict
        self.data.energy_per_year = base_energy_df
        
        # Build events tables
        all_strategies = outputWP6['eventTables [-]']
        total_ops = 0
        
        if all_strategies['CaBaMa_eventsTable'].isnull().values.all():
            
            calendar_events_df = None
            
        else:
            
            raw_df = all_strategies['CaBaMa_eventsTable']
            calendar_events_df = get_events_table(raw_df)
            total_ops += len(calendar_events_df)
            
        if all_strategies['CoBaMa_eventsTable'].isnull().values.all():
            
            condition_events_df = None
            
        else:
            
            raw_df = all_strategies['CoBaMa_eventsTable']
            condition_events_df = get_events_table(raw_df)
            total_ops += len(condition_events_df)

        if all_strategies['UnCoMa_eventsTable'].isnull().values.all():
            
            corrective_events_df = None
            
        else:
            
            raw_df = all_strategies['UnCoMa_eventsTable']
            corrective_events_df = get_events_table(raw_df)    
            total_ops += len(corrective_events_df)
                
        self.data.calendar_maintenance_events = calendar_events_df
        self.data.condition_maintenance_events = condition_events_df
        self.data.corrective_maintenance_events = corrective_events_df
        self.data.journeys = total_ops
        
        return
