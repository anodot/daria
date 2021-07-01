from pysnmp.hlapi.v1arch import *


def extract_metrics():
    iterator = getCmd(
        SnmpDispatcher(),
        CommunityData('public', mpModel=0),
        UdpTransportTarget(('demo.snmplabs.com', 161)),
        ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)),
        lookupMib=True
    )

    for response in iterator:
        errorIndication, errorStatus, errorIndex, varBinds = response
        if errorIndication:
            print(errorIndication)
        elif errorStatus:
            print('%s at %s' % (
                errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'
            ))
        else:
            for varBind in varBinds:
                print(' = '.join([x.prettyPrint() for x in varBind]))
