#!/bin/bash
import argparse
import os
import re
import socket
from urlparse import urlparse
from mimetypes import MimeTypes


def open_file(f):
    file = open(f, 'r')
    content = file.read()
    return content

#execute GET
def get(args):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    parsedurl = urlparse(args.url)
    s.connect((parsedurl.netloc, 80))
    
    #initial Request
    currentRequest = '\r\n'.join(('GET '+parsedurl.path+"?"+parsedurl.query+' HTTP/1.1','Host: '+parsedurl.netloc))
    
    #add headers
    if args.h:
        for h in args.h: 
            currentRequest = '\r\n'.join((currentRequest, h))
    request = '\r\n'.join((currentRequest, '', ''))
    s.send(request)
    response = s.recv(8192)
    s.close()

    #parse response
    response = response.split('{', 1)
    header = response[0]
    if args.v: print (header) 
    print('{'+response[1])

#execute POST
def post(args):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    parsedurl = urlparse(args.url)
    s.connect((parsedurl.netloc, 80))

    #initial Request
    currentRequest = '\r\n'.join(('POST '+parsedurl.path+"?"+parsedurl.query+' HTTP/1.1','Host: '+parsedurl.netloc))
    
    #add headers and data
    if args.h:
        for h in args.h: 
            currentRequest = '\r\n'.join((currentRequest, h))

    if args.d: 
        length = len(args.d)
        currentRequest = '\r\n'.join((currentRequest, 'Content-Length:'+str(length)))
        request = '\r\n'.join((currentRequest, '',args.d, ''))

    elif args.f:
       mime = MimeTypes()
       currentRequest = '\r\n'.join((currentRequest, 'Content-Length:'+str(os.stat(args.f).st_size/4)))
       currentRequest = '\r\n'.join((currentRequest, 'Content-Type:'+mime.guess_type(args.f)[0]))
       request = '\r\n'.join((currentRequest, '',"@"+open_file(args.f), ''))

    else: 
        request = '\r\n'.join((currentRequest, '', ''))

    s.send(request)
    response = s.recv(8192)
    s.close()

    #parse response
    response = response.split('{', 1)
    header = response[0]
    if args.v: print (header) 
    print('{'+response[1])

#validate Header input
def valid_header(h):
    if re.match("[A-Za-z0-9-]*:[A-Za-z0-9-]*", h):
        return h
    else: 
        msg = "Not a valid Header: '{0}'.".format(h)
        raise argparse.ArgumentTypeError(msg)


#define argparse parsers
parser = argparse.ArgumentParser(prog='httpc', conflict_handler='resolve', description="httpc is a curl-like application but supports HTTP protocol only.", 
epilog="Use \"httpc [command] --help\"  for more information about a command.")

subparsers = parser.add_subparsers()
#define GET arguments
parser_get = subparsers.add_parser('get', conflict_handler='resolve', help="executes a HTTP GET request and prints the response.", description="Get executes a HTTP GET request for a given URL.")
parser_get.add_argument('-h', help="Associates headers to HTTP Request with the format 'key:value'.", nargs='?', type=valid_header)
parser_get.add_argument('-v', help="Prints the detail of the response such as protocol, status, and headers.", action="store_true", default=False)
parser_get.add_argument('url', type=str, help="URL for the request", default="httpbin.org")
parser_get.set_defaults(func=get)

#define POST arguments
parser_post = subparsers.add_parser('post', conflict_handler='resolve', help="executes a HTTP POST request and prints the response.", description="Post executes a HTTP POST request for a given URL with inline data or from"
+"file.", epilog="Either [-d] or [-f] can be used but not both.")
group = parser_post.add_mutually_exclusive_group()
group.add_argument('-d', help="Associates an inline data to the body HTTP POST request.", type=str, nargs='?')
group.add_argument('-f', help="Associates the content of a file to the body HTTP POST request.", type=str, nargs='?')
parser_post.add_argument('-h', help="Associates headers to HTTP Request with the format 'key:value'.", nargs='?', type=valid_header)
parser_post.add_argument('-v', help="Prints the detail of the response such as protocol, status, and headers.", action="store_true", default=False)
parser_post.add_argument('url', type=str, help="URL for the request", default="httpbin.org")
parser_post.set_defaults(func=post)

#define non specific arguments



#parse and call appropriate function
args = parser.parse_args()
args.func(args)
