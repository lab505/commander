 # coding:utf-8
"""
任务数据实体
"""

import json, logging
import PyQt5, PyQt5.QtWidgets
import mission_widget
from mission_planning import mission_planning

class Fly_Mission():
    """
    飞行任务(Fly_Mission)
    一个飞行区域(Area)中可以有很多个飞行任务
    """
    def __init__(self, rc, name, area, mission_attribute):
        self.rc = rc
        self.name = name
        self.area = area
        self.mission_attribute = mission_attribute
        self.son_mission_widget_items = []
        self.rubber_bands = []
        self.mission_widget_item = self.create_mission_widget_item()
        self.create_rubber_bands()

    @staticmethod
    def create_from_text(rc, area, text_):
        try:
            dic_ = json.loads(text_)
            assert dic_['type'] == 'Fly_Mission'
            fly_mission_ = Fly_Mission(rc, dic_['name'], area, dic_['mission_attribute'])
            return True, fly_mission_
        except Exception as e:
            logging.exception(e)
            return False, None
    
    def to_text(self):
        return json.dumps(self.mission_attribute)
    
    def delete(self):
        self.hide()
        del self.rubber_bands[:]
        for item in self.son_mission_widget_items:
            item.parent.removeChild(item)
        self.mission_widget_item.parent.removeChild(self.mission_widget_item)
        del self.area.missions[self.name]
        del self
        
    def create_mission_widget_item(self):
        item = mission_widget.Mission_Widget_Item(
            rc=self.rc,
            parent=self.area.mission_widget_item,
            type_='fly_mission',
            binding_object=self
        )
        item.setExpanded(True)
        return item
    
    def create_polyline_rubber_band(self, name, polyline, color, width, line_style):
        rubber_band = self.rc.gis_canvas.show_temp_polyline_from_points_list(
            polyline,
            'EPSG:4326',
            color=color, width=width, line_style=line_style)
        rubber_band.name = name
        self.rubber_bands.append(rubber_band)
        item = mission_widget.Mission_Widget_Item(
            rc=self.rc,
            parent=self.mission_widget_item,
            type_='geometry',
            binding_object=rubber_band
        )
        self.son_mission_widget_items.append(item)
    
    def create_points_rubber_band(self, name, points, color, width, line_style):
        rubber_band = self.rc.gis_canvas.show_temp_points_from_points_list(
            points,
            'EPSG:4326',
            color=color, width=width)
        rubber_band.name = name
        self.rubber_bands.append(rubber_band)
        item = mission_widget.Mission_Widget_Item(
            rc=self.rc,
            parent=self.mission_widget_item,
            type_='geometry',
            binding_object=rubber_band
        )
        self.son_mission_widget_items.append(item)

    def create_rubber_bands(self):
        mission_area = self.mission_attribute[0]['mission_area']
        mission_area = mission_area[:] + mission_area[:1]
        for i in range(len(self.mission_attribute)):
            aerocraft_mission = self.mission_attribute[i]
            shoot_coors_geo = []
            for coor in aerocraft_mission['route_coors']:
                x, y = coor['longitude'], coor['latitude']
                shoot_coors_geo.append((x, y))
            self.create_polyline_rubber_band(
                name='航线%d' % i,
                polyline=shoot_coors_geo,
                color=PyQt5.QtCore.Qt.blue,
                width=2,
                line_style=PyQt5.QtCore.Qt.SolidLine)
            self.create_points_rubber_band(
                name='拍摄点%d' % i,
                points=shoot_coors_geo,
                color=PyQt5.QtCore.Qt.green,
                width=2,
                line_style=PyQt5.QtCore.Qt.SolidLine)
        board_region = [(p_['longitude'], p_['latitude']) for p_ in self.mission_attribute[0]['board_region']]
        self.create_polyline_rubber_band(
            name='任务区域',
            polyline=mission_area,
            color=PyQt5.QtCore.Qt.red,
            width=1,
            line_style=PyQt5.QtCore.Qt.DashLine)
        self.create_polyline_rubber_band(
            name='可飞行区域',
            polyline=board_region,
            color=PyQt5.QtCore.Qt.yellow,
            width=2,
            line_style=PyQt5.QtCore.Qt.DashLine)
    
    def showtype(self):
        print(self.mission_attribute)

    def show(self):
        if 'mission_widget_item' in dir(self):
            if self.mission_widget_item.checkState(0) != PyQt5.QtCore.Qt.Checked:
                self.mission_widget_item.setCheckState(0, PyQt5.QtCore.Qt.Checked)
        for item in self.son_mission_widget_items:
            item.set_checked(True)
    
    def hide(self):
        if 'mission_widget_item' in dir(self):
            if self.mission_widget_item.checkState(0) != PyQt5.QtCore.Qt.Unchecked:
                self.mission_widget_item.setCheckState(0, PyQt5.QtCore.Qt.Unchecked)
        for item in self.son_mission_widget_items:
            item.set_checked(False)

class Area():
    """
    飞行区域(Area)
    """
    def __init__(self, rc, name, polygon):
        self.rc = rc
        self.name = name
        self.polygon = polygon
        self.missions = {}
        #self.rubber_band = self.rc.gis_canvas.show_temp_polygon_from_points_list(
        #    self.polygon, 'EPSG:4326', edgecolor=PyQt5.QtCore.Qt.black, fillcolor=PyQt5.QtCore.Qt.blue)
        self.rubber_band = self.rc.gis_canvas.show_temp_polyline_from_points_list(
            self.polygon[:]+self.polygon[:1], 'EPSG:4326', color=PyQt5.QtCore.Qt.gray, width=2)
        self.mission_widget_item = self.rc.mission_widget.add_area(self)
    
    @staticmethod
    def create_from_text(rc, area, text_):
        try:
            dic_ = json.loads(text_)
            assert dic_['type'] == 'Area'
            area_ = Area(rc, dic_['name'], dic_['polygon'])
            missions = dic_['missions']
            for mission_name in missions:
                succ, ret = Fly_Mission.create_from_text(rc, area, missions[mission_name])
                assert succ
                area.missions[mission_name] = ret
            return True, area_
        except Exception as e:
            logging.exception(e)
            return False, None
    
    def to_text(self):
        text_missions = {}
        for mission_name in self.missions:
            text_missions[mission_name] = self.missions[mission_name].to_text()
        dic_ = {
            'type': 'Area',
            'name': self.name,
            'polygon': self.polygon,
            'missions': text_missions,
        }
        return json.dumps(dic_)
    
    def show(self):
        if 'mission_widget_item' in dir(self):
            if self.mission_widget_item.checkState(0) != PyQt5.QtCore.Qt.Checked:
                self.mission_widget_item.setCheckState(0, PyQt5.QtCore.Qt.Checked)
        self.rubber_band.show()
    
    def hide(self):
        if 'mission_widget_item' in dir(self):
            if self.mission_widget_item.checkState(0) != PyQt5.QtCore.Qt.Unchecked:
                self.mission_widget_item.setCheckState(0, PyQt5.QtCore.Qt.Unchecked)
        self.rubber_band.hide()
        
    def create_fly_mission(self, mission_attribute):
        newmission_name = mission_attribute[0]['mission_name']
        if newmission_name in self.missions:
            return False, 'ERROR:该区域已有同名任务 %s' % newmission_name
        newmission = Fly_Mission(self.rc, mission_attribute[0]['mission_name'], self, mission_attribute)
        self.missions[newmission_name] = newmission
        self.hide()
        return True, None
    
    def delete(self):
        self.hide()
        for mission_name in list(self.missions.keys()):
            self.missions[mission_name].delete()
        del self.mission_widget_item
        self.rc.mission_manager.del_area(self.name)
        del self
            
class MissionManager():
    """
    任务管理器
    可以包含很多个飞行区域
    """
    def __init__(self, rc):
        self.rc = rc
        self.rc.mission_manager = self
        self.areas = {}
    
    def add_area(self, area_name, area_polygon):
        if area_name in self.areas:
            return False, 'area_name %s alread in areas' % area_name
        
        newarea = Area(self.rc, area_name, area_polygon)
        self.areas[area_name] = newarea
        self.rc.fly_mission_widget.init_areas()
        return True, newarea
    
    def del_area(self, area_name):
        self.rc.fly_mission_widget.init_areas()
        del self.areas[area_name]
    
    def add_fly_mission_to_area(self, params):
        area_name = params['area_name']
        area = self.areas.get(area_name, None)
        if area is None:
            return False, '不存在的区域:%s' % area_name
        succ, ret = mission_planning.mission_planning(
            area_points_list=area.polygon,
            mission_name=params['mission_name'],
            aerocraft=params['aerocraft'],
            camera=params['cameras'],
            ground_resolution_m=params['ground_resolution_m'],
            forward_overlap=params['forward_overlap'],
            sideway_overlap=params['sideway_overlap'],
            fly_direction=params['fly_direction'],
            application=params['application'],
            aerocraft_num=params['aerocraft_num'],
            )
        if not succ:
            return False, ret
        else:
            mission_attribute = ret
            succ, ret = area.create_fly_mission(mission_attribute)
            if not succ:
                return False, ret
            else:
                return True, ''
