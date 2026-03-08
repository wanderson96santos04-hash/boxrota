# Estrutura correta para seu marketplace
#
# Seu catálogo precisa ter tipos de veículos.
#
# Tabela parts deveria ter algo assim:
#
# id | name | sku | vehicle_type
# 1  | Filtro de óleo | FILTRO-OLEO | car
# 2  | Filtro de óleo moto | FILTRO-OLEO-MOTO | moto
# 3  | Pastilha freio | PASTILHA-FREIO | car
# 4  | Pastilha freio moto | PASTILHA-MOTO | moto
#
# Assim o sistema separa.

# Peças comuns de CARRO
#
# Categorias principais:
# - Filtro de óleo
# - Filtro de ar
# - Filtro cabine
# - Velas
# - Pastilha de freio
# - Disco de freio
# - Amortecedor
# - Correia dentada
# - Correia alternador
# - Bomba combustível
# - Radiador
# - Sensor oxigênio
# - Bateria
# - Rolamento
# - Embreagem

# Peças comuns de MOTO
#
# Agora as peças de moto que você precisa no catálogo:
# - Kit relação (corrente + coroa + pinhão)
# - Pastilha freio moto
# - Disco freio moto
# - Filtro de ar moto
# - Filtro óleo moto
# - Velas moto
# - Bateria moto
# - Cabo acelerador
# - Cabo embreagem
# - Coroa
# - Pinhão
# - Corrente transmissão
# - Amortecedor moto
# - Retentor bengala
# - Kit embreagem moto

# Essas são as mais vendidas em oficinas de moto.

# Exemplo real no marketplace
#
# Oficina digita:
# CG 160
#
# Sistema sugere:
# - Velas NGK
# - Kit relação
# - Pastilha freio dianteira
# - Filtro ar moto
# - Bateria
#
# Clica em kit relação:
#
# Auto Peças Centro
# Marca: DID
# R$ 129,90
# Em estoque

# Como gerar 3000 peças incluindo moto
#
# Divisão simples:
# - 2000 peças carro
# - 1000 peças moto

# Categorias carro
# 15 categorias * 130 variações = 1950 peças

# Categorias moto
# 10 categorias * 100 variações = 1000 peças

# Total aproximado: 2950 peças

# Exemplo de peças de moto geradas:
# - Kit relação CG 160
# - Kit relação YBR 125
# - Kit relação Fazer 250
# - Kit relação Titan 150
# - Kit relação Bros 160
# - Pastilha freio CG 160
# - Pastilha freio XRE 300
# - Pastilha freio Fazer 250
# - Filtro ar CG 160
# - Filtro ar Titan 150
# - Filtro ar Biz 125

# Só CG + Titan + Biz + Fazer já geram centenas.

# Isso deixa seu SaaS muito mais forte
#
# Porque você atende:
# - Oficina carro
# - Oficina moto
# - Oficina mista
#
# No Brasil isso é muito comum.