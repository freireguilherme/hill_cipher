import numpy as np
from egcd import egcd
import argparse

alfabeto = "" + (chr(10))

for i in range(32, 127):
    alfabeto += chr(i)
for i in range(160, 255):
    alfabeto += (chr(i))

letra_index = dict(zip(alfabeto,  range(len(alfabeto)))) # 'a':0, 'b':1 ... 'z':25
index_letra = dict(zip(range(len(alfabeto)), alfabeto))  # 0:'a', 1:'b'... 25:'z'


def matriz_mod_inv(matriz, modulo):
    '''Para encontrar a matriz inversa em modulo precisamos
    Passo 1) Encontrar o determinante
    Passo 2) Encontrar o valor inverso do determinante em modulo, para um modulo especifico
    Passo 3) Resolvemos (inverso do determinante) vezes o (determinante * matriz_inversa modulo m)'''
    
    det = int(np.round(np.linalg.det(matriz))) #passo 1. Usamos algebra linear do numpy para isso. Arrendodamos e garantimos q seja int
    inv_det = egcd(det, modulo)[1] % modulo    #passo 2. Aqui usamos egcd para o algoritmo euclidiano extendido
    inv_matriz_modulo = inv_det * np.round(det * np.linalg.inv(matriz)).astype(int) % modulo #passo 3
    
    return inv_matriz_modulo

def encrypt(mensagem, K):
    '''Recebe um texto claro e uma matriz chave K,
        e retorna um texto cifrado de hill'''

    encriptografado = ''
    mensagem_em_numeros = []
    
    #Tornar a mensagem em numeros
    for letra in mensagem:
        mensagem_em_numeros.append(letra_index[letra])
        
    
    #Separar em tamanho da matriz K
    separar_TextoClaro = [mensagem_em_numeros[i:i+int(K.shape[0])] for i in range(0, len(mensagem_em_numeros), int(K.shape[0]))]
    
    #Passa por cada parte da mensagem e encriptar usando K*P(mod m)
    for P in separar_TextoClaro:
        P = np.transpose(np.asarray(P))[:, np.newaxis] #precisa adicionar uma nova dimensão
        
        while P.shape[0] != K.shape[0]:                        #se o texto a ser cifrado é menor q a chave
            P = np.append(P, letra_index[' '])[:, np.newaxis]  #completa com espaço em branco ' '

        numeros = np.dot(K, P) % len(alfabeto)                  # K . P (produto vetorial)

        n = numeros.shape[0] #n = número de colunas da matriz

        #Tornar numeros em letras     
        for idx in range(n):
            numero = int(numeros[idx])
            encriptografado += index_letra[numero]

    return encriptografado

def decrypt (cifra, Kinv):
    '''Recebe um texto cifrado de hill e
    e uma matriz inversa da matriz K'''

    decifrado = ''
    cifra_em_numeros = []
    
    #Tornar mensagem cifrada em numeros
    for letra in cifra:
        cifra_em_numeros.append(letra_index[letra])
    
    #Separar em tamanho da matriz inversa K
    separar_TextoCifrado = [cifra_em_numeros[i:i + int(Kinv.shape[0])] for i in range(0, len(cifra_em_numeros), int(Kinv.shape[0]))]
    
    #Iterar por cada cifra parcial e decriptar usando inv(K)*C (mod 26)
    for C in separar_TextoCifrado:
        C = np.transpose(np.asarray(C))[:, np.newaxis]
        numeros = np.dot(Kinv, C) % len(alfabeto)
        n = numeros.shape[0]
    
    #Tornar numeros em letras
        for idx in range(n):
            numero = int(numeros[idx])
            decifrado += index_letra[numero]

    return decifrado


def main():
    '''Por meio de argumentos, informa se é motivo de encriptar ou decifrar, o nome do arquivo de 
    texto em txt a ser manipulado e o nome do arquivo de texto txt onde será a saída
    
    o texto de entrada pode conter esses caracteres:
    " !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~ ¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþ"
    Um exemplo de como passar os argumentos para encriptar usando cifra de hill:
    cifrahill.py --enc textoclaro.txt --out textocifrado.txt
    
    Exemplo para decifrar
    cifrahill.py --dec textocifrado.txt --out textoclaro.txt'''

    parser = argparse.ArgumentParser(
    prog="Cifra de hill",
    description="recebe um arquivo txt e devolve um arquivo txt. Se --enc, encripta. Se --dec, decifra. Uso: cifrahill.py --enc textoclaro.txt --out textocifrado.txt para cifrar. cifrahill.py --dec textocifrado.txt --out textoclaro.txt. O nome do arquivo nao importa",
    epilog = "Programa para encriptar ou decifrar por meio da cifra de hill. As opcoes sao --enc, --dec, --out ",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-e", "--enc", action="store", type=str, help="encripta texto")
    parser.add_argument("-d", "--dec", action="store", type=str, help="decripta texto")
    parser.add_argument("-o", "--out", action="store", type=str, help="arquivo de saída")

    #K = np.array([[3,3],[2,5]]) #chave para alfabeto 26 letras
    #mensagem = 'elementos de criptografia e seguranca cifra de hill'
    
    K = np.matrix([[3,10,20],[28,19,17],[23,78,17]]) #para alfabeto 27 letras (26 letras + ' '). A matriz precisa ser tal q K * K^-1 = matriz identidade
    
    args = parser.parse_args()
    try:
        if (args.enc):
            with open(args.enc, 'r') as arquivo:
                texto = arquivo.readlines()

            mensagem_cifrada = encrypt("".join(texto), K)
            with open(args.out, mode='w') as arquivo:
                arquivo.writelines(mensagem_cifrada)

        elif(args.dec):
            with open(args.dec, 'r') as arquivo:
                texto = arquivo.readlines()
            Kinv = matriz_mod_inv(K, len(alfabeto))
            mensagem_decifrada = decrypt("".join(texto), Kinv)
            with open(args.out, mode='w') as arquivo:
                arquivo.writelines(mensagem_decifrada)

        else:
            print('opcção inválida. tente -h ou --help')
    except UnicodeEncodeError as error:
        print(error)
        print("Nao foi possivel, talvez algum caractere no texto de entrada nao pôde ser interpretado.")
    except KeyError as error:
        print(error)
        print("Nao foi possivel, talvez algum caractere no texto de entrada nao pôde ser interpretado.")
    except FileNotFoundError as error:
        print(error)
        print("Arquivo de entrada nao localizado")
main()