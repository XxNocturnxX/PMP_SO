#!/usr/bin/env python
import os.path
import sys
import ConfigParser
import ast
import socket
import re
import pmp_so_utils

check_fs = re.compile("/{1,2}[-_A-Za-z0-9]*(/[-_A-Za-z0-9]*)*")

def check_config_file(config_file, set_values=False):
    servidores = {}
    errors = False

    config = ConfigParser.RawConfigParser()
    config.read(config_file)

    section_genopt = config.options('opciones')
    section_opciones.sort()

    section_servers = config.options('servidores')
    section_servers.sort()

    section_mantenimiento = config.options('mantenimiento')
    section_mantenimiento.sort()

    print "Verificando archivo de cofiguracion " + config_file

    for server in section_servers:
        try:
            aux_dict = ast.literal_eval(config.get('servidores', server))

            if 'ip' not in aux_dict:
                print "\tEl " + server + " no tiene especificado el campo 'ip'"
                errors = True
                continue

            if 'hostname' not in aux_dict:
                print "\tEl " + server + " no tiene especificado el campo 'hostname'"
                errors = True
                continue
            
            if set_values:
                servidores[aux_dict['ip']] = {
                        'hostname'  : aux_dict['hostname'],
                        'cpu_usr'   : [70,80],
                        'cpu_sys'   : [75,85],
                        'mem_ram'   : [80,90],
                        'mem_swap'  : [25,50],
                        'red'       : 50,
                        'filesys'   : [80,90]
                    }
            
            for k, v in aux_dict.iteritems():
                if k=='ip':
                    try:
                        socket.inet_aton(v)
                    except socket.error as err:
                        print "\tLa ip del " + server + " no es valida."
                        errors = True

                elif k=='hostname':
                    if not pmp_so_utils.is_valid_hostname(v):
                        print "\tEl hostname del " + server + " no es valido."
                        errors = True

                elif k=='red': 
                    if (type(v) is not int or ( 0 > v or v > 100 )):
                        print "\tEl valor del umbral de red para el " + server + " no es valido."
                        errors = True
                    
                    if set_values:
                        servidores[aux_dict['ip']]['red'] = aux_dict['red']

                elif k in ['cpu_usr', 'cpu_sys', 'mem_ram', 'mem_swap', 'filesys'] or check_fs.match(k): 

                    if type(v) is not list:
                        print "\tError de sintaxis en los umbrales de '" + k + "' en el " + server + "."
                        errors = True
                        continue

                    if len(v) != 2:
                        print "\tDeben especificarse dos umbrales para el atributo '" + k + "' en el " + server + "."
                        errors = True
                        continue

                    if type(v[0]) is not int or type(v[1]) is not int or v[0] > v[1] or v[0] < 0 or v[1] > 100:
                        print "\tLos umbrales de '" + k + "' para el " + server + " no son validos."
                        errors = True
                        continue
                    
                    if set_values:
                        servidores[aux_dict['ip']][k] = aux_dict[k]
                else:
                    print "\tOpcion '" + k + "' no valida en la definicion del " + server + "."
                    errors = True


            #print aux_dict
        except SyntaxError as inst:
            print "\tError de sintaxis en la definicion del " + server + "."
            errors = True

    for ventana in section_mantenimiento:
        aux_dict = ast.literal_eval(config.get('mantenimiento', ventana))

        for k, v in aux_dict.iteritems():
            if k == 'ip':
               
                if type(v) is not list:
                    print "\tError de sintaxis en las ip de la " + ventana + "."
                    errors = True
                    continue

                for ip in aux_dict['ip']:
                    try:
                        socket.inet_aton(v)
                    except socket.error as err:
                        print "\tLa ip '" + ip + "' de la " + ventana + " no es valida."
                        errors = True

             elif k == 'inicio' or k == 'fin':
                try:
                    pmp_so_utils.validate(v)
                except ValueError as err:
                    errors = True
                    print err

             else
                print "\tOpcion '" + k + "' no valida en la definicion del " + server + "."
                errors = True
    
    if errors:
        print "Verifique el archivo de configuracion.\n"
        exit(1)

    if set_values:
        print "Archivo de configuracion valido. Caracteristicas establecidas para " + str(len(section_servers)) + " servidores."
        return servidores
    print "Archivo de configuracion valido. Se verificaron " + str(len(section_servers)) + " servidores."
    exit(0)

def get_attr(server_ip, attr):
    return servidores[server_ip][attr]

config_file = sys.argv[1]

if not os.path.isfile(config_file) and not os.path.exists(config_file):
    print "El archivo de configuracion no existe o es invalido.\n"
    exit(1)

servidores = check_config_file(config_file,True)

print get_attr('10.66.151.247','hostname')
print get_attr('10.66.151.247','cpu_usr')
print get_attr('10.66.151.247','cpu_sys')
print get_attr('10.66.151.247','mem_swap')
print get_attr('10.66.151.247','mem_ram')
print get_attr('10.66.151.247','red')
print get_attr('10.66.151.247','filesys')