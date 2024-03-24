
import hashlib
import json
from requests import get, post

class HttpConection():
    """__init__() functions as the class constructor"""
    def __init__(self, IP, PIN):
        # Variables
        self.deviceStates = [];                 # Used to internally buffer the retrieved states before writing them to the adapter
        self.noOfConnectionErrors = 0           # Counter for connection problems
        self.missingState = False               # If a device state cannot be mapped to an internal state of the adapter, this variable gets set
        self.timer = 0                          # Settimeout-Pointer to the poll-function
        self.disableAdapter = False             # If an error occurs, this variable is set to true which disables the adapter
        self.hw_version = 0                     # Hardware version retrieved from the device
        self.sw_version = 0                     # Software version retrieved from the device
        self.hpin = self.calculateHPIN(PIN)     # HPIN is the 'encrypted' PIN of the device
        self.hspin = 0                          # HSPIN is the secret, depending on the current NONCE and the HPIN
        self.nonce = 0                          # The current NONCE of the device
        self.adapter = 0                        # Adapter object
        # self.pin = PIN                          # PIN of the device
        self.prg = ''
        self.mode = ''
        self.ip = IP
        self.url = 'http://' + IP + '/status.cgi'
        self.headers = {}
        
    # Handle a state change
    def handleStateChange(self, id, state):
        # Warning, state can be null if it was deleted
        print('stateChange ' + id + ' ' + state)
        
        # you can use the ack flag to detect if it is status (true) or command (false)
        # if (state and not state.ack):
        print('stateChange (command): ' + id + ' ' + state)
        post_data_prg = '{"prg":' + state + '}'
        self.createHeader(post_data_prg)
        
        r = post(self.url, data=post_data_prg, headers=self.headers)
        print('Post response: {}'.format(r.content))
        
        # if String(id) is (adapter.namespace + '.device.prg'):
        #         # Set new program
        #
        #
        #         # Perform request
        #         request.post({
        #             headers: ,
        #             url:     self.url,
        #             body:    post_data_prg
        #         }, def(error, response, body):
        #             print('POST response: ' + response + ' [RESPONSE]; ' + body + ' [BODY]; ' + error + ' [ERROR];')
        #
        #             # POST was successful, perform ack
        #         if error is None and response.statusCode is 200:
        #                 # Acknowledge command
        #                 adapter.setState(adapter.namespace + '.device.prg', state.val, true);
        #             # POST was not successful, revert
        #             else:
        #                 print('stateChange (command): ' + id + ' ' + (state) + ' was not successful')
        #                 print('POST response: ' + response + ' [RESPONSE]; ' + body + ' [BODY]; ' + error + ' [ERROR];')
        #
        #
        #             # Poll new state to update nonce immediately
        #             pollDeviceStatus()
        #         )
        # elif String(id) is (adapter.namespace + '.device.sp_temp'):
        #         # Set new program
        #     const post_data_sp_temp = '{"sp_temp":' + state.val + '}'
        #
        #         # Perform request
        #         request.post({
        #             headers: createHeader(post_data_sp_temp),
        #             url:     'http://' + adapter.config.fireplaceAddress + '/status.cgi',
        #             body:    post_data_sp_temp
        #         }, function(error, response, body):
        #             print('POST response: ' + response + ' [RESPONSE]; ' + body + ' [BODY]; ' + error + ' [ERROR];')
        #
        #             # POST was successful, perform ack
        #             if error is None and response.statusCode is 200:
        #                 # Acknowledge command
        #                 adapter.setState(adapter.namespace + '.device.sp_temp', state.val, true);
        #             # POST was not successful, revert
        #             else:
        #                 print('stateChange (command): ' + id + ' ' + JSON.stringify(state) + ' was not successful')
        #                 print('POST response: ' + response + ' [RESPONSE]; ' + body + ' [BODY]; ' + error + ' [ERROR];')
        #
        #
        #             # Poll new state to update nonce immediately
        #             pollDeviceStatus()
        #         )

        
    def syncState(self, state, path):
        print('Syncing state of the oven')
        
        try:
            # Iterate all elements
            for item in state:   
                print(item)
                print('{}'.format(type(state[item])))
                if item == 'error':
                    print('{}'.format(item))
                if isinstance(state[item], dict | list):
                    for subitem in state[item]:
                        print('{}: {}'.format(item, subitem))

            print('Nonce: {}'.format(state['meta']['nonce']))
            print('Mode: {}'.format(state['mode']))
            self.prg = state['prg']
            self.mode = state['mode']
            self.nonce = state['meta']['nonce']
            self.hspin = self.calculateHSPIN(self.nonce, self.hpin)
            
        except Exception as e:
            # Dump error and stop adapter
            print('Error syncing states: {}'.format(e))
            self.disableAdapter = True

    # Main function to poll the device status
    def pollDeviceStatus(self):
        response = get(self.url)
        print('{}'.format(response.text))
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
    # Given the HPIN and the current NONCE, the HSPIN is calculated
    # HSPIN = MD5(NONCE + HPIN)
    def calculateHSPIN(self, NONCE, HPIN):
        result = hashlib.md5(NONCE + HPIN);
        print('HSPIN: {}'.format(HPIN));
        return result;
    
    # The PIN of the device is used to calculate the HPIN
    # HPIN = MD5(PIN)
    def calculateHPIN(self, PIN):
        result = hashlib.md5(PIN);
        print('HPIN: {}'.format(result));
        return result;
    
    def createHeader(self, post_data):
        self.headers = {
            'Host':    self.ip,
            'Accept':    '*/*',
            'Proxy-Connection':    'keep-alive',
            'X-BACKEND-IP':    'https://app.haassohn.com',
            'Accept-Language': 'de-DE;q=1.0, en-DE;q=0.9',
            'Accept-Encoding': 'gzip;q=1.0, compress;q=0.5',
            'token': '32bytes',
            'Content-Type': 'application/json',
            'Content-Length': str(len(post_data)),
            'User-Agent': 'ios',
            'Connection':    'keep-alive',
            'X-HS-PIN': str(self.hspin)
            }
         
            
def main():
    parser = HttpConection() 
    parser.pollDeviceStatus()
    print('Done!\n')
if __name__ == '__main__':
    main()
    
