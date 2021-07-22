To enable `sasl.kerberos.domain.name` in kafka client, follow next steps:

1. Clone `https://github.com/apache/kafka.git` repository.

2. Navigate to `clients/src/main/java/org/apache/kafka/common/config/SaslConfigs.java` class and add next lines:

```java
 public static final String SASL_KERBEROS_DOMAIN_NAME = "sasl.kerberos.domain.name";
 public static final String SASL_KERBEROS_DOMAIN_NAME_DOC = "The Kerberos principal domain name that Kafka runs as. "
            + "This can be defined either in Kafka's JAAS config or in Kafka's config.";

.... omitted for clarity...


public static void addClientSaslSupport(ConfigDef config) {
        config.define(SaslConfigs.SASL_KERBEROS_SERVICE_NAME, ConfigDef.Type.STRING, null, ConfigDef.Importance.MEDIUM, SaslConfigs.SASL_KERBEROS_SERVICE_NAME_DOC)
              .define(SaslConfigs.SASL_KERBEROS_DOMAIN_NAME, ConfigDef.Type.STRING, null, ConfigDef.Importance.MEDIUM, SaslConfigs.SASL_KERBEROS_DOMAIN_NAME_DOC)

.... omitted for clarity...

```
3. Navigate to clients/src/main/java/org/apache/kafka/common/network/SaslChannelBuilder.java, and add next lines to method `org.apache.kafka.common.network.SaslChannelBuilder#buildChannel`
```java

String krbDomainName = (String) configs.get(SaslConfigs.SASL_KERBEROS_DOMAIN_NAME);
boolean krbDomainNameSet = krbDomainName != null && krbDomainName.trim().length() > 0;
log.info("{} configured={}. Value={}", SaslConfigs.SASL_KERBEROS_DOMAIN_NAME, krbDomainNameSet, krbDomainName);

authenticator = buildClientAuthenticator(configs,
                        saslCallbackHandlers.get(clientSaslMechanism),
                        id,
                        krbDomainNameSet ? krbDomainName : socketChannel.socket().getInetAddress().getHostName(),
                        loginManager.serviceName(),
                        transportLayer,
                        subjects.get(clientSaslMechanism));
```

Full method looks like this:

```java
    @Override
    public KafkaChannel buildChannel(String id, SelectionKey key, int maxReceiveSize, MemoryPool memoryPool) throws KafkaException {
        try {
            SocketChannel socketChannel = (SocketChannel) key.channel();
            Socket socket = socketChannel.socket();
            TransportLayer transportLayer = buildTransportLayer(id, key, socketChannel);
            Authenticator authenticator;

            String krbDomainName = (String) configs.get(SaslConfigs.SASL_KERBEROS_DOMAIN_NAME);
            boolean krbDomainNameSet = krbDomainName != null && krbDomainName.trim().length() > 0;
            log.info("{} configured={}. Value={}", SaslConfigs.SASL_KERBEROS_DOMAIN_NAME, krbDomainNameSet, krbDomainName);


            if (mode == Mode.SERVER) {
                authenticator = buildServerAuthenticator(configs,
                        saslCallbackHandlers,
                        id,
                        transportLayer,
                        subjects);
            } else {
                LoginManager loginManager = loginManagers.get(clientSaslMechanism);
                authenticator = buildClientAuthenticator(configs,
                        saslCallbackHandlers.get(clientSaslMechanism),
                        id,
                        krbDomainNameSet ? krbDomainName : socketChannel.socket().getInetAddress().getHostName(),
                        loginManager.serviceName(),
                        transportLayer,
                        subjects.get(clientSaslMechanism));
            }
            return new KafkaChannel(id, transportLayer, authenticator, maxReceiveSize, memoryPool != null ? memoryPool : MemoryPool.NONE);
        } catch (Exception e) {
            log.info("Failed to create channel due to ", e);
            throw new KafkaException(e);
        }
    }
```
4. Build jar file
```shell script
./gradlew :clients:jar
```

    
                
                








