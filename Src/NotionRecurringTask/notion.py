import base64
import json
import requests
import logging

class NotionAPIClient:
    def __init__(self, base_url,auth):
        self.user = ''
        self.password = ''
        if not base_url.endswith('/'):
            base_url += '/'
        self.__url = base_url + 'v1/' 
        self.__auth=auth              

    def send_get(self, uri, filepath=None):
        """Issue a GET request (read) against the API.

        Args:
            uri: The API method to call including parameters, e.g. get_case/1.
            filepath: The path and file name for attachment download; used only
                for 'get_attachment/:attachment_id'.

        Returns:
            A dict containing the result of the request.
        """
        return self.__send_request('GET', uri, filepath)

    def send_post(self, uri, data):
        """Issue a POST request (write) against the API.

        Args:
            uri: The API method to call, including parameters, e.g. add_case/1.
            data: The data to submit as part of the request as a dict; strings
                must be UTF-8 encoded. If adding an attachment, must be the
                path to the file.

        Returns:
            A dict containing the result of the request.
        """
        return self.__send_request('POST', uri, data)
    
    def send_patch(self, uri, data):
        return self.__send_request('PATCH', uri, data)

    def __send_request(self, method, uri, data):
        url = self.__url + uri

        # auth = str(
        #     base64.b64encode(
        #         bytes('%s:%s' % (self.user, self.password), 'utf-8')
        #     ),
        #     'ascii'
        # ).strip()        
        auth=self.__auth
        headers = {'Authorization': 'Bearer ' + auth}
        headers['Notion-Version'] = '2022-02-22'
        headers['Content-Type'] = 'application/json'
        status_code=0
        looptime=0
        error=""
        while((status_code>201 and looptime<3) or status_code==0 ):
            looptime=looptime+1
            if status_code>201 and looptime<3:
                logging.info("Notion request retry {0} time(s)".format(looptime))            
            if method == 'POST':
                # if uri[:14] == 'add_attachment':    # add_attachment API method
                #     files = {'attachment': (open(data, 'rb'))}
                #     response = requests.post(url, headers=headers, files=files)
                #     files['attachment'].close()
                # else:
            
            
                payload = bytes(json.dumps(data), 'utf-8')
                response = requests.post(url, headers=headers, data=payload,verify=False)
            elif method=='PATCH':
                payload = bytes(json.dumps(data), 'utf-8')
                response = requests.patch(url, headers=headers, data=payload,verify=False)
            else:           
                response = requests.get(url, headers=headers,verify=False)
            status_code=response.status_code
            if status_code > 201:
                try:
                    error = response.json()
                except:     # response.content not formatted as JSON
                    error = str(response.content)
                logging.warning('Notion API returned HTTP %s (%s)' % (response.status_code, error))
                # raise APIError('Notion API returned HTTP %s (%s)' % (response.status_code, error))
            else:
                # if uri[:15] == 'get_attachment/':   # Expecting file, not JSON
                #     try:
                #         open(data, 'wb').write(response.content)
                #         return (data)
                #     except:
                #         return ("Error saving attachment.")
                # else:
                try:
                    return response.json()
                except: # Nothing to return
                    return {}
        if status_code>201 and looptime>=3:
            logging.error('Notion API returned HTTP %s (%s)' % (response.status_code, error))       

class APIError(Exception):
    pass
