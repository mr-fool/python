import eventlet
from eventlet import wsgi 
from eventlet.green import time
from urllib.parse import urlparse
import urllib.request
import operator

#Database constant
datas = ['hello', 'world']

#different comparators BBsql uses
comparators = ['<','=','>','false']

def parse_response(env, start_response):
    try:
        params =  urllib.parse_qs.unquote(env['QUERY_STRING'])

        #Extract out all the sqli information

        row_index = int(params['row_index'].pop(0))
        char_index = int(params['character_index'].pop(0))
        test_char = int(params['character_value'].pop(0))
        comparator = comparators.index(params['comparator'].pop(0)) - 1
        sleep_int = int(params['sleep'].pop(0))

        #determine which character postiion we are at during injection

        current_character = datas[row_index][char_index]

        #call the function for what path was given based on the path provided
        response = types[env['PATH_INFO']](test_char, current_character, comparator, sleep_int, start_response)

        return response
    
    except:
        start_response('400 Bad Request',[ ('Content-Type', 'text/plain')] )
        return ['error\r\n']
    
    
def time_based_blind(test_char, current_character, comparator, sleep_int, start_response):
    try: 
        truth = operator.eq(test_char, ord(current_character)) == comparator
        sleep_time = float(sleep_int) * truth
        time.sleep(sleep_time)
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return ['Hello!\r\n']
    except:
        start_response('400 Bad Request',[('Content-Type', 'text/plain')] )
        return ['error\r\n']

def boolean_based_error(test_char, current_character, comparator, env, start_response):
    try:
        truth = operator.eq(test_char, ord(current_character)) == comparator
        if truth: 
            start_response('200 OK', [('Content-Type', 'text/plain')] )
            return ['Hello, we are doing great\r\n']
        else: 
            start_response('404 File Not found', [('Content-Type', 'text/plain')])
            return ['file not found error\r\n']
    except: 
        start_response('400 Bad Request', [('Content-Type', 'text/plain')])

def boolean_based_size(test_char, current_character, comparator, env, start_response):
    try: 
        truth = operator.eq(test_char, ord(current_character)) == comparator
        if truth: 
            start_response('200 OK', [('Content-Type', 'text/plain')] )
            return ['Hello, you submitted a query and match was found\r\n']
        else: 
            start_response('400 Bad Request', [('Content-Type', 'text/plain')])
            return ['error\r\n']
    except: 
        start_response('400 Bad Request', [('Content-Type', 'text/plain')]) 


#Dict of the types of tests

types = {'/time':time_based_blind,'/error':boolean_based_error,'/boolean':boolean_based_size} 

# Start the server
print ("\n")
print ("bbqsql http server\n\n")
print ("used to unit test boolean, blind, and error based sql injection")
print ("path can be set to /time,  /error, or /boolean")
print ("\n")

