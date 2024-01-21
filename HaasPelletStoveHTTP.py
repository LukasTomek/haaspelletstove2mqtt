from requests import get
import json

class HttpConection():
    """__init__() functions as the class constructor"""
    def __init__(self, IP):
        # Variables
        self.deviceStates = [];                 # Used to internally buffer the retrieved states before writing them to the adapter
        self.noOfConnectionErrors = 0;       # Counter for connection problems
        self.missingState = False;           # If a device state cannot be mapped to an internal state of the adapter, this variable gets set
        self.timer = 0;                          # Settimeout-Pointer to the poll-function
        self.disableAdapter = False;         # If an error occurs, this variable is set to true which disables the adapter
        self.hw_version = 0;                     # Hardware version retrieved from the device
        self.sw_version = 0;                     # Software version retrieved from the device
        self.hpin = 0;                           # HPIN is the 'encrypted' PIN of the device
        self.hspin = 0;                          # HSPIN is the secret, depending on the current NONCE and the HPIN
        self.nonce = 0;                          # The current NONCE of the device
        self.adapter = 0;                        # Adapter object
        self.mode = '';
        self.url = 'http://' + IP + '/status.cgi'
    def syncState(self, state, path):
        print('Syncing state of the oven')
        
        try:
            # Iterate all elements
            for item in state:   
                print(item)
                print(type(state[item]))
                if item == 'error':
                    print(item)
                if isinstance(state[item], dict | list):
                    for subitem in state[item]:
                        print('{}: {}'.format(item, subitem))

            print('Nonce: {}'.format(state['meta']['nonce']))
            print('Mode: {}'.format(state['mode']))
            self.mode = state['mode']
        except Exception as e:
            # Dump error and stop adapter
            print('Error syncing states: ' + e)
            self.disableAdapter = True

    # Main function to poll the device status
    def pollDeviceStatus(self):
        response = get(self.url)
        print(response.text)
        if response.status_code == 200:
    
            try:
                # Evaluate result
                result = json.loads(response.text)
    
                # Reset error counter
                self.noOfConnectionErrors = 0
    
                # Sync states
                self.syncState(result, '')
            except Exception as e:
                # Parser error
                print('Error parsing the response: {}'.format(e))
    
                # Increment error counter
                self.noOfConnectionErrors += 1
    
        else:
            # Connection error
            # print'Error retrieving status: ' + error)
    
            # Increment error counter
            self.noOfConnectionErrors += 1
    
    
        # Update connection status
        # updateConnectionStatus()
    
            # Poll again, except a critical error occurred
            # if not disableAdapter:
            #     timer = setTimeout(def(){
            #         pollDeviceStatus()
            #     }, adapter.config.pollingInterval * 1000)
            # }
        # Synchronize the retrieved states with the states of the adapter
    
def main():
    parser = HttpConection() 
    parser.pollDeviceStatus()
    print('Done!\n')
if __name__ == '__main__':
    main()
    