'''
********************************************************************************
* Name: Project Generation Tests
* Author: Alan D. Snow
* Created On: February 28, 2017
* License: BSD 3-Clause
********************************************************************************
'''
from glob import glob
from os import path
import unittest
from shutil import copy

from .template import TestGridTemplate

from gsshapy.orm import (ProjectFile, WatershedMaskFile, ElevationGridFile,
                         MapTableFile)
from gsshapy.lib import db_tools as dbt

from os import path, chdir

class TestProjectGenerate(TestGridTemplate):
    def setUp(self):
        self.compare_path = path.join(self.readDirectory,
                                      'phillipines',
                                      'compare_data')

        self.gssha_project_directory = self.writeDirectory

        self.shapefile_path = path.join(self.writeDirectory,
                                        'phillipines_5070115700.shp')

        self.elevation_path = path.join(self.writeDirectory,
                                        'gmted_elevation.tif')
        self.land_use_grid = path.join(self.writeDirectory, 'LC_hd_global_2012.tif')

        # copy shapefile
        shapefile_basename = path.join(self.readDirectory,
                                       'phillipines',
                                       'phillipines_5070115700.*')

        for shapefile_part in glob(shapefile_basename):
            try:
                copy(shapefile_part,
                     path.join(self.writeDirectory, path.basename(shapefile_part)))
            except OSError:
                pass

        # copy elevation grid
        try:
            copy(path.join(self.readDirectory, 'phillipines',
                           'gmted_elevation.tif'),
                 self.elevation_path)
        except OSError:
            pass

        # copy land cover data
        try:
            copy(path.join(self.readDirectory, 'land_cover', 'LC_hd_global_2012.tif'),
                 self.land_use_grid)
        except OSError:
            pass

        # Create Test DB
        sqlalchemy_url, sql_engine = dbt.init_sqlite_memory()

        # Create DB Sessions
        self.db_session = dbt.create_session(sqlalchemy_url, sql_engine)

        chdir(self.gssha_project_directory)

    def _compare_masks(self, mask_name):
        '''
        compare mask files
        '''
        new_mask_grid = path.join(self.writeDirectory, mask_name)
        compare_msk_file = path.join(self.compare_path, mask_name)
        self._compare_files(compare_msk_file, new_mask_grid, raster=True)

    def _before_teardown(self):
        '''
        Method to execute at beginning of tearDown
        '''
        self.db_session.close()

    def test_generate_basic_project(self):
        '''
        Tests generating a basic GSSHA project
        '''

        project_name = "grid_standard_basic"
        # Instantiate GSSHAPY object for reading to database
        project_manager = ProjectFile(name=project_name, map_type=1)
        self.db_session.add(project_manager)
        self.db_session.commit()

        # ADD MASK
        mask_name = '{0}.msk'.format(project_name)
        msk_file = WatershedMaskFile(project_file=project_manager,
                                     session=self.db_session)

        msk_file.generateFromWatershedShapefile(self.shapefile_path,
                                                mask_name,
                                                x_cell_size=1000,
                                                y_cell_size=1000,
                                                )

        # ADD ELEVATION FILE
        ele_file = ElevationGridFile(project_file=project_manager,
                                     session=self.db_session)
        ele_file.generateFromRaster(self.elevation_path)

        # ADD OUTLET POINT
        grid = project_manager.getGrid()
        lon, lat = grid.pixel2lonlat(0,6)

        project_manager.setOutlet(latitude=lat, longitude=lon,
                                  outslope=0.002)

        # ADD ADDITIONAL REQUIRED FILES
        # see http://www.gsshawiki.com/Project_File:Required_Inputs
        project_manager.setCard('TOT_TIME', '180')
        project_manager.setCard('TIMESTEP', '10')
        project_manager.setCard('HYD_FREQ', '15')
        # see http://www.gsshawiki.com/Project_File:Output_Files_%E2%80%93_Required
        project_manager.setCard('SUMMARY', '{0}.sum'.format(project_name), add_quotes=True)
        project_manager.setCard('OUTLET_HYDRO', '{0}.otl'.format(project_name), add_quotes=True)
        # see http://www.gsshawiki.com/Project_File:Overland_Flow_%E2%80%93_Required
        project_manager.setCard('MANNING_N', '0.0013')
        # see http://www.gsshawiki.com/Project_File:Rainfall_Input_and_Options_%E2%80%93_Required
        project_manager.setCard('PRECIP_UNIF', '')
        project_manager.setCard('RAIN_INTENSITY', '2.4')
        project_manager.setCard('RAIN_DURATION', '30')
        project_manager.setCard('START_DATE', '2017 02 28')
        project_manager.setCard('START_TIME', '14 33')

        # write data
        project_manager.writeInput(session=self.db_session,
                                   directory=self.gssha_project_directory,
                                   name=project_name)
        # compare msk
        self._compare_masks(mask_name)
        # compare ele
        ele_grid_name = '{0}.ele'.format(project_name)
        new_mask_grid = path.join(self.gssha_project_directory, ele_grid_name)
        compare_msk_file = path.join(self.compare_path, ele_grid_name)
        self._compare_files(compare_msk_file, new_mask_grid, raster=True)
        # compare project files
        prj_file_name = '{0}.prj'.format(project_name)
        generated_prj_file = path.join(self.gssha_project_directory, prj_file_name)
        compare_prj_file = path.join(self.compare_path, prj_file_name)
        self._compare_files(generated_prj_file, compare_prj_file)
        # check to see if projection file generated
        proj_file_name = '{0}_prj.pro'.format(project_name)
        generated_proj_file = path.join(self.gssha_project_directory, proj_file_name)
        compare_proj_file = path.join(self.compare_path, proj_file_name)
        self._compare_files(generated_proj_file, compare_proj_file)

    def test_generate_basic_project_land_cover(self):
        '''
        Tests generating a basic GSSHA project with land cover
        '''

        project_name = "grid_standard_basic_land_cover"
        # Instantiate GSSHAPY object for reading to database
        project_manager = ProjectFile(name=project_name, map_type=1)
        self.db_session.add(project_manager)
        self.db_session.commit()

        # ADD MASK
        mask_name = '{0}.msk'.format(project_name)
        msk_file = WatershedMaskFile(project_file=project_manager,
                                     session=self.db_session)

        msk_file.generateFromWatershedShapefile(self.shapefile_path,
                                                mask_name,
                                                x_cell_size=1000,
                                                y_cell_size=1000,
                                                )

        # ADD ELEVATION FILE
        ele_file = ElevationGridFile(project_file=project_manager,
                                     session=self.db_session)
        ele_file.generateFromRaster(self.elevation_path)

        # ADD OUTLET POINT
        grid = project_manager.getGrid()
        lon, lat = grid.pixel2lonlat(0,6)

        project_manager.setOutlet(latitude=lat, longitude=lon,
                                  outslope=0.002)

        # ADD ROUGHNESS FROM LAND COVER
        # see http://www.gsshawiki.com/Project_File:Overland_Flow_%E2%80%93_Required
        mapTableFile = MapTableFile(project_file=project_manager)
        mapTableFile.addRoughnessMapFromLandUse("roughness",
                                                self.db_session,
                                                self.land_use_grid,
                                                land_use_grid_id='glcf',
                                                )

        # ADD ADDITIONAL REQUIRED FILES
        # see http://www.gsshawiki.com/Project_File:Required_Inputs
        project_manager.setCard('TOT_TIME', '180')
        project_manager.setCard('TIMESTEP', '10')
        project_manager.setCard('HYD_FREQ', '15')
        # see http://www.gsshawiki.com/Project_File:Output_Files_%E2%80%93_Required
        project_manager.setCard('SUMMARY', '{0}.sum'.format(project_name), add_quotes=True)
        project_manager.setCard('OUTLET_HYDRO', '{0}.otl'.format(project_name), add_quotes=True)
        # see http://www.gsshawiki.com/Project_File:Rainfall_Input_and_Options_%E2%80%93_Required
        project_manager.setCard('PRECIP_UNIF', '')
        project_manager.setCard('RAIN_INTENSITY', '2.4')
        project_manager.setCard('RAIN_DURATION', '30')
        project_manager.setCard('START_DATE', '2017 02 28')
        project_manager.setCard('START_TIME', '14 33')

        # write data
        project_manager.writeInput(session=self.db_session,
                                   directory=self.gssha_project_directory,
                                   name=project_name)
        # compare msk
        self._compare_masks(mask_name)
        # compare ele
        ele_grid_name = '{0}.ele'.format(project_name)
        new_mask_grid = path.join(self.gssha_project_directory, ele_grid_name)
        compare_msk_file = path.join(self.compare_path, ele_grid_name)
        self._compare_files(compare_msk_file, new_mask_grid, raster=True)
        # compare cmt
        cmt_file_name = '{0}.cmt'.format(project_name)
        new_cmt_file = path.join(self.gssha_project_directory, cmt_file_name)
        compare_cmt_file = path.join(self.compare_path, cmt_file_name)
        self._compare_files(new_cmt_file, compare_cmt_file)
        # compare idx
        new_idx_file = path.join(self.gssha_project_directory, 'roughness.idx')
        original_idx_file = path.join(self.compare_path, 'roughness.idx')
        self._compare_files(original_idx_file, new_idx_file, raster=True)
        # compare project files
        prj_file_name = '{0}.prj'.format(project_name)
        generated_prj_file = path.join(self.gssha_project_directory, prj_file_name)
        compare_prj_file = path.join(self.compare_path, prj_file_name)
        self._compare_files(generated_prj_file, compare_prj_file)
        # check to see if projection file generated
        proj_file_name = '{0}_prj.pro'.format(project_name)
        generated_proj_file = path.join(self.gssha_project_directory, proj_file_name)
        compare_proj_file = path.join(self.compare_path, proj_file_name)
        self._compare_files(generated_proj_file, compare_proj_file)

if __name__ == '__main__':
    unittest.main()