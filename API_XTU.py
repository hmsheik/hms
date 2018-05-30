'''This API class is for an agent that want to discover/communicate/monitor/control
prolon Vav '''
import socket
from DeviceAPI.ModbusAPI import ModbusAPI
from bemoss_lib.utils.BEMOSS_ONTOLOGY import BEMOSS_ONTOLOGY
from bemoss_lib.protocols.Modbus import connection
import csv
import os
debug = True
_Timeout=15

class API(ModbusAPI):
    def __init__(self, **kwargs):
        super(API, self).__init__(**kwargs)
        self.set_variable('connection_renew_interval', 6000)
        self.device_supports_auto = True
        if 'address' in self.variables.keys():
            address_parts = self.get_variable("address").split(':')
            self.address = address_parts[0]
            self.slave_id =int(address_parts[1])
        self._debug = True


    def API_info(self):
        return [{'device_model' : 'XTENDER 8000-48', 'vendor_name' : 'XTU', 'communication' : 'Modbus',
                'device_type_id' : 4,'api_name': 'API_XTU','html_template':'inverter/solar.html',
                'agent_type':'BasicAgent','identifiable' : False, 'authorizable': False, 'is_cloud_device' : False,
                'schedule_weekday_period' : 4,'schedule_weekend_period' : 4, 'allow_schedule_period_delete' : False,
                'chart_template': 'charts/charts_solar.html'}]

    def dashboard_view(self):
        return {"top": None, "center": {"type": "meter", "value": BEMOSS_ONTOLOGY.ENERGY_TOTAL.NAME, "unit": 'MWH'},
                "bottom": BEMOSS_ONTOLOGY.VOLTAGE_L1.NAME,"image":"PV.png"}

    def ontology(self):
        return { "Total yield": BEMOSS_ONTOLOGY.ENERGY_TOTAL,"DC voltage": BEMOSS_ONTOLOGY.VOLTAGE_DC, "DC current": BEMOSS_ONTOLOGY.CURRENT_DC,
                "AC active power": BEMOSS_ONTOLOGY.POWER_AC, "Power frequency":BEMOSS_ONTOLOGY.FREQUENCY,
                "Grid voltage L1": BEMOSS_ONTOLOGY.VOLTAGE_L1,"Grid voltage L2": BEMOSS_ONTOLOGY.VOLTAGE_L2,  "Grid current L1": BEMOSS_ONTOLOGY.CURRENT_AC,
                }

    def getDataFromDevice(self):

            try:
                device_data={}
                client = connection(self.address, port=502)
                name="inverter"
                if not hasattr(self, "data"):
                    config_path = os.path.dirname(os.path.abspath(__file__))
                    config_path = config_path + "/Modbusdata/" + name + ".csv"
                    with open(os.path.join(config_path), 'rU') as infile:
                        reader = csv.DictReader(infile)
                        data = {}
                        for row in reader:
                            for header, value in row.items():
                                try:
                                    data[header].append(value)
                                except KeyError:
                                    data[header] = [value]
                    self.data = data
                device_count = self.data["Type"]
                device_map = self.duplicates_indices(device_count)
                scale={}
                for device, values in device_map.iteritems():
                    if device == "energy":
                        energy = self.collectdata(client, values, 30533, 1,scale)
                        for k, v in energy.iteritems():
                            device_data[k] = v
                    elif device =="others":
                        others = self.collectdata(client, values, 30769, 40,scale)
                        for k, v in others.iteritems():
                            device_data[k] = v

                return device_data

            except Exception as er:
                print "classAPI_ModPowerMeter: ERROR: Reading Modbus registers at getDeviceStatus:"
                print er
                return None



    def getSignedNumber(self,number,limit):
        mask = (2 ** limit) - 1
        if number & (1 << (limit - 1)):
            return number | ~mask
        else:
            return number & mask


def main():
    #Utilization: test methods
    #Step1: create an object with initialized data from DeviceDiscovery Agent
    #requirements for instantiation1. model, 2.type, 3.api, 4. address,
    Inv = API(model='XTU',type='inverter',api='API_XTU',address='78.188.64.34:1')

    #Inv.getDeviceStatus()

    Inv.discover()

if __name__ == "__main__": main()
