# Keep on Track

O Keep on Track é um projeto de monitoramento de ronda de funcionários utilizando beacons e Raspberry PI.

Fornecendo beacons bluetooth para cada funcionário, conseguimos medir a distância do funcionário de cada Raspberry PI e assim acompanhar suas rondas em seu turno e melhorar sua assertividade no trabalho, possibilitando a supervisão ou gerência monitorar e assegurar o cumprimento de SLAs dos locais que devem ser monitorados, seja por time de segurança, bombeiro ou supervisão técnica, apresentando os pontos de checagem em um dashboard em tempo real.

No Raspberry, que possui o Linux Debian Reference 2.98 como sistema operacional, é executado o código do arquivo "read_beacon_data.py" presente neste repositório, que monitora os sinais bluetooth dos beacons e envia seus dados para o Azure Hub IoT via protocolo MQTT, o Azure Hub Iot envia os dados para o Azure Stream Analytics que envio os dados em tempo real para um dashboard construído com o Microsoft Power BI.

<br />

# Materiais

Nesta seção você encontrará todos os hardwares utilizados para a produção do projeto.

<br />

## C6 IBEACON & EDDYSTONE

O iBeacon & Eddystone (dispositivo de transmissão digital) C6 é projetado com base no Bluetooth de baixa energia 4.0; é uma etiqueta utilizável que suporta prendê-la a alguém por meio de um cordão de pescoço ou chaveiro. O C6 transmite os dados em intervalos regulares e ajustáveis de acordo com o protocolo iBeacon padrão da Apple.

<br />

## RASPBERRY PI 3 MODEL B+

A Raspberry Pi 3 Model B+ Anatel é um mini-PC que roda distribuições Linux como o Raspbian e Ubuntu, mas também suporta outros sistemas operacionais como o Windows 10 IoT e versões customizadas do Linux.

A versão B+ da Raspberry Pi 3 tem processador de 1.4GHz, 1GB de memória e suporta redes wireless no padrão AC, proporcionando muito mais velocidade para a sua conexão. Essas especificações, aliadas à outras melhorias no conjunto do hardware, fazem com que essa placa tenha uma performance 17% maior em comparação ao modelo anterior.

<strong>Especificações:</strong>
- Raspberry Pi 3 Model B+ Anatel
- Processador Broadcom BCM2837B0 64bits ARM Cortex-A53 Quad-Core
- Clock 1.4 GHz
- Memória RAM: 1GB
- Adaptador Wifi 802.11 b/g/n/AC 2.4GHz e 5GHz integrado
- Bluetooth 4.2 BLE integrado
- Conector de vídeo HDMI
- 4 portas USB 2.0
- Conector Gigabit Ethernet over USB 2.0 (throughput máximo de 300 Mbps)
- Alimentação: Fonte DC chaveada 5V 3A
- Interface para câmera (CSI)
- Interface para display (DSI)
- Slot para cartão microSD
- Conector de áudio e vídeo
- GPIO de 40 pinos
- Certificado de homologação Anatel: 01598-18-10629
- Dimensões: 85 x 56 x 17mm

<br />

## Case com cooler para Raspberry 3 modelo B+ (Opcional)

<strong>Cooler</strong>
- Tensão nominal: 5V;
- Tensão de funcionamento: 4.5 a 5V;
- Volume de dispersão de ar: 5m³/h;
- Número de rotação: 13200 RPM;
- Ruído: 18 dB;
- Dimensões: 30 x 30 x 10mm (comprimento x largura x altura);

<strong>Case</strong>
- Cor: Preto;
- Material: Plástico ABS;
- Fixação: Pinos para encaixes;
- Refrigeração: Perfurações para na tampa, base e em uma das laterais para auxiliar no escoamento do calor;
- Dimensões do produto: 66 x 92 x 32mm (largura x comprimento x altura);

<br />

## Fonte 5Vcc 3A Micro USB

Micro usb 5v 3a 3000ma ac para dc fonte de alimentação adaptador eua ue plug on/off interruptor 100v 240v conversor carregador de parede para raspberry pi

<strong>Especificações:</strong>

- 100v-240v ac à fonte de alimentação do adaptador da c.c.
- Entrada: 100-240vac 0.3a 50/60hz
- Saída: 5v3a
- Tamanho da tomada da c.c. (diâmetro exterior & diâmetro interno): micro usb
- Plug especificações: plugue da ue
- Comprimento do cabo: 90cm
- Cor: preto
- Tamanho: 95mm x 68mm x 40mm
- Peso líquido: 90g

<br />

## Cartão de Memória

Cartão de Memória 32GB Ultra Micro SD Classe 10 SDSQUNS-GN3MA SanDisk

<strong>Características:</strong>

- Tipo: micro SD
- Classe: 10
- Velocidade de Leitura: 80MB/s
- Ideal para smartphones e tablets
- Capacidade para armazenar gravação e reprodução Full HD
- Capacidade de armazenamento 32GB

<br />

# Softwares 

Nesta seção é apresentado o sistema operacional executado no Raspberry Pi 3 Model B+, o framework de desenvolvimento, os pacotes de reconhecimento bluetooth, o SDK de desenvolvimento do Azure Hub Iot, o Azure Hub Iot, o Azure Stream Analytics e o Microsoft Power BI.

<br />

## Raspberry Pi Desktop for PC

Debian com Raspberry Pi Desktop é o nosso sistema operativo. 
Para instalar o sistema opecional no cartão de memória utilize o manual oficial em `https://www.raspberrypi.com/software/`

<br />

## Python 3

Python é uma linguagem Open-Source de propósito geral usado bastante em data science, machine learning, desenvolvimento de web, desenvolvimento de aplicativos, automação de scripts, fintechs e mais.

Para instalar o Python utilize o comando abaixo no terminal de comando do Raspberry Pi Desktop for PC:

`sudo apt-get install python3-pip`

<br />

## Pacotes de reconhecimento bluetooth

São pacotes do Raspberry Pi Desktop for PC que permitem o reconhecimento de dispositivos bluetooth e que são utilizados no script que envia os dados dos beacons ao servidor MQTT (Azure Hub IoT)

Para instalar os pacotes de reconhecimento bluetooth utilize os comandos abaixo no terminal de comando do Raspberry Pi Desktop for PC:

`sudo apt-get install libbluetooth-dev bluez`

`sudo pip3 install pybluez`

<br />

## SDK do Azure Hub IoT

É um SDK disponibilizado pela Microsof Azure que auxilia o envio de mensagens ao Azure Hub Iot utilizando o protocolo MQTT.

Para instalar o SDK do Azure Hub IoT utilize o comando abaixo no terminal de comando do Raspberry Pi Desktop for PC:

`sudo pip3 install azure-iot-device`

<br />

## Azure Hub IoT

O Hub IoT do Azure é uma ferramenta para habilitar a comunicação entre soluções IoT, que possui comunicação utilizando protocolo MQTT, possibilitando assim a troca de dados entre dispositivos e aplicações IoT. 

O Azure Hub Iot é um recurso do Microsoft Azure que possui uma câmada de utilização gratuita para até 8.000 mensagens por dia. Para sua utilização deve ser criada uma conta no Microsoft Azure.

Para o recebimento das mensagens, o dispositivos Raspberry Pi 3 Model B+ devem ser cadastrados no Azure Hub Iot. Após o seu cadastro, o id do dispositivo deverá ser utilizado na string de conexão utilizada no script que deve ser instalado e executado no Raspberry Pi 3 Model B+.

<br />

## Azure Stream Analytics

O Azure Stream Analytics é uma ferramenta de análise de dados em tempo real, projetada para receber cargas de dados críticas, possibilitando assim a criação de um pipeline streaming e serverless de ponta a ponta.

No Azure Stream Analytics também é um recurso do Microsoft Azure, mas este não possui camada gratuita. Nele deve ser configurado uma entrada de dados com a origem sendo o Azure Hub Iot e uma saída de dados apontado para o Microsoft Power BI.

<br />

## Microsof Power BI

O Power BI é uma ferramenta de BI (Business Intelligence) utilizada para unificar e escalonar dados para inteligência de negócio dentro do mundo corporativo, ajudando a obter insights mais aprofundados sobre os dados analisados.

O Microsoft Power BI é uma ferramenta da microsoft e possui uma versão gratuita. Nele deve ser criado um relatório para apresentar as informações e uma origem de dados no formato Stream.

<br />

> As configurações do Azure Hub Iot, Azure Stream Analytics e Microsoft Power BI devem ser realizadas conforme exemplo disponibilizado em `https://learn.microsoft.com/pt-br/azure/iot-hub/iot-hub-live-data-visualization-in-power-bi`

<br />

# Comunicação

O Raspberry Pi 3 Model B+ se comunica com os beacons através de conexão bluetooth, necessita de uma conexão wifi para estabelecer conexão com a internet e envia os dados para o servidor via protocolo MQTT.

<br />

# Documentação e Execução do Código

O arquivo read_beacons_data.py é um script escrito na linguagem Python utilizado para identificar os beacons bluetooth e enviar seus dados para o Azure Hub Iot via protocolo MQTT.

Para sua execução é necessário possuir o Python 3 instalado na máquina, os pacotes bluetooth e SDK do Azure Hub Iot, conforme listados acima.

Para o envio dos dados ao Azure Hub IoT, cada Raspberry Pi 3 Model B+ deve ser cadastrado no Azure Hub IoT para que seja gerado o seu id. Esse id deve ser utilizado na string de conexão existente no script na linha 23. Além do id do dispositivo, deve ser fornecido o HostName e a SharedAccessKey, que podem ser capturadas no menu "Pontos de extremidade internos" no Azure Hub Iot.

Após a configuração da string de conexão, o script deve ser executado pelo terminal de comando do Raspberry Pi Desktop for PC utilizando o seguinte código na pasta onde está localizado o script:

`sudo python3 read_beacons_data.py`
