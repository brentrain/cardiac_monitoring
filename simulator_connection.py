import serial
import serial.tools.list_ports
import time
import json
from flask import Blueprint, jsonify, request
from threading import Thread, Lock

simulator_bp = Blueprint('simulator', __name__)

class ProSim8Connection:
    def __init__(self):
        self.serial_port = None
        self.is_connected = False
        self.ecg_data = []
        self.data_lock = Lock()
        self.connection_thread = None
        self.running = False

    def list_available_ports(self):
        """List all available serial ports."""
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append({
                'device': port.device,
                'description': port.description,
                'manufacturer': port.manufacturer if hasattr(port, 'manufacturer') else None
            })
        return ports

    def connect(self, port=None, baudrate=9600):
        try:
            # If no port specified, try to auto-detect ProSim 8
            if port is None:
                ports = self.list_available_ports()
                for p in ports:
                    # Look for ports that might be the ProSim 8
                    # You may need to adjust this based on how the ProSim 8 identifies itself
                    if 'USB' in p['description'].upper() or 'SERIAL' in p['description'].upper():
                        port = p['device']
                        break
                
                if port is None:
                    return False, "No suitable serial port found. Please connect ProSim 8 and try again."

            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            self.is_connected = True
            self.running = True
            self.connection_thread = Thread(target=self._read_data)
            self.connection_thread.daemon = True
            self.connection_thread.start()
            return True, f"Successfully connected to ProSim 8 on port {port}"
        except Exception as e:
            return False, f"Failed to connect to ProSim 8: {str(e)}"

    def disconnect(self):
        self.running = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.is_connected = False
        if self.connection_thread:
            self.connection_thread.join()

    def _read_data(self):
        while self.running:
            try:
                if self.serial_port.in_waiting:
                    # Read ECG data from ProSim 8
                    # Format: 2 bytes for each ECG sample (12-bit resolution)
                    data = self.serial_port.read(2)
                    if len(data) == 2:
                        # Convert bytes to voltage value
                        # ProSim 8 outputs 12-bit values (0-4095) representing -5V to +5V
                        value = int.from_bytes(data, byteorder='big')
                        voltage = (value - 2048) * (10.0 / 4096.0)  # Convert to voltage
                        
                        with self.data_lock:
                            self.ecg_data.append(voltage)
                            # Keep only last 6 seconds of data (3000 samples at 500Hz)
                            if len(self.ecg_data) > 3000:
                                self.ecg_data.pop(0)
            except Exception as e:
                print(f"Error reading from ProSim 8: {str(e)}")
                time.sleep(0.1)

    def get_ecg_data(self):
        with self.data_lock:
            return self.ecg_data.copy()

    def get_connection_status(self):
        return {
            "connected": self.is_connected,
            "port": self.serial_port.port if self.serial_port else None,
            "samples": len(self.ecg_data)
        }

# Create a global instance of the connection
prosim_connection = ProSim8Connection()

@simulator_bp.route('/ports', methods=['GET'])
def list_ports():
    """Endpoint to list available serial ports."""
    ports = prosim_connection.list_available_ports()
    return jsonify({"ports": ports})

@simulator_bp.route('/connect', methods=['POST'])
def connect_simulator():
    """Connect to the simulator with optional port specification."""
    data = request.get_json() or {}
    port = data.get('port', None)  # If not specified, will try auto-detection
    success, message = prosim_connection.connect(port=port)
    return jsonify({"success": success, "message": message})

@simulator_bp.route('/disconnect', methods=['POST'])
def disconnect_simulator():
    prosim_connection.disconnect()
    return jsonify({"success": True, "message": "Disconnected from ProSim 8"})

@simulator_bp.route('/status', methods=['GET'])
def get_status():
    return jsonify(prosim_connection.get_connection_status())

@simulator_bp.route('/ecg_data', methods=['GET'])
def get_ecg_data():
    return jsonify(prosim_connection.get_ecg_data()) 