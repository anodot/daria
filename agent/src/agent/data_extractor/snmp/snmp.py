from pysnmp.entity.engine import SnmpEngine
from pysnmp.hlapi import getCmd, CommunityData, UdpTransportTarget, ContextData
from pysnmp.smi.rfc1902 import ObjectType, ObjectIdentity
from agent.pipeline import Pipeline


def extract_metrics(pipeline_: Pipeline):
    # todo does it have timeout?
    iterator = getCmd(
        SnmpEngine(),
        # todo auth is somewhere here
        CommunityData('public', mpModel=0),
        UdpTransportTarget(('localhost', 1161)),
        ContextData(),
        ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysUpTime', 0)),
        ObjectType(ObjectIdentity('1.3.6.1.2.1.55.1.5.1.10.1')),
        ObjectType(ObjectIdentity('1.3.6.1.2.1.55.1.5.1.3.1')),
        # lookupMib=True
    )

    for response in iterator:
        errorIndication, errorStatus, errorIndex, varBinds = response
        if errorIndication:
            print(errorIndication)
            return
        elif errorStatus:
            print('%s at %s' % (
                errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'
            ))
            return
        for varBind in varBinds:
            a = varBind[0]
            b = varBind[1]
            t = 1
