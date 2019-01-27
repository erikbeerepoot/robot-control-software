import serial
import tenacity


class SerialPort:
    '''
    This class provides a wrapper around PySerial's serial class to handle reties & some errors
    '''

    @tenacity.retry(wait=tenacity.wait_fixed(5),
                    stop=tenacity.stop_after_attempt(3))
    def __init__(self):
        self.port = serial.Serial()

    def open(self, port_name, baud_rate=115200, timeout=0.1):
        '''
        Open a serial port with appropriate default settings for the robot
        '''
        self.port.baudrate = baud_rate
        self.port.timeout = timeout
        self.port.port = port_name
        self.port.parity = serial.PARITY_NONE

        if self.port.is_open:
            print("Port already open!")
            self.port.close()

        try:
            self.port.open()
        except ValueError:
            print("Passed invalid parameter while attempting to open serial port. Check port params.")
        except serial.serialutil.SerialException as e:
            print("Exception occurred while attempting to open the serial port.")
            print(f"Ex: {e}")
            self.handle_serial_port_failure(e)
            raise e
        except Exception as e:
            print("Exception occurred while attempting to open the serial port.")
            print(f"Ex: {e}")
            self.handle_serial_port_failure(e)
            raise e

    def handle_serial_port_failure(self, ex):
        '''
        Check the type of failure and handle appropriately by logging hints or closing the port
        '''
        if str(ex).find("device disconnected or multiple access on port?") > 0:
            self.port.is_open = False
        elif str(ex).find("Invalid argument") > 0:
            print("Received invalid argument. This usually means the serial port wasn't closed properly.")

    def read_all(self, chunk_size=200):
        """Read all characters on the serial port and return them."""
        if not self.port.timeout:
            raise TypeError('Port needs to have a timeout set!')

        read_buffer = b''

        while True:
            try:
                byte_chunk = self.port.read(chunk_size)
                read_buffer += byte_chunk
                if not len(byte_chunk) == chunk_size:
                    break
            except serial.serialutil.SerialException as e:
                print(f"Exception occurred during serial port read. Exception: {e}")
                self.handle_serial_port_failure(e)
                break
        return read_buffer

    def close(self):
        '''
        Close the serial port
        :return: Status of port (True if open, False if closed)
        '''
        self.port.close()
        return self.port.is_open
